import logging
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

import uvicorn
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import jobs, pipeline
from .settings import Settings, get_settings
from .database import get_db

logger = logging.getLogger(__name__)


def ensure_directories(settings: Settings) -> None:
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.TMP_DIR, exist_ok=True)


def _build_params(
    preset: Optional[str],
    steps: Optional[int],
    guidance: Optional[float],
    octree_resolution: Optional[int],
    settings: Settings,
) -> Dict[str, Any]:
    preset_name = (preset or settings.DEFAULT_PRESET).lower()
    if preset_name not in settings.PRESETS:
        raise HTTPException(status_code=422, detail=f"Invalid preset '{preset_name}'")

    base = dict(settings.PRESETS[preset_name])
    resolved = {
        "preset": preset_name,
        "steps": steps if steps is not None else base["steps"],
        "guidance": guidance if guidance is not None else base["guidance"],
        "octree_resolution": octree_resolution
        if octree_resolution is not None
        else base["octree"],
    }

    if not (settings.MIN_STEPS <= resolved["steps"] <= settings.MAX_STEPS):
        raise HTTPException(
            status_code=422,
            detail=f"steps must be between {settings.MIN_STEPS} and {settings.MAX_STEPS}",
        )
    if not (settings.MIN_OCTREE <= resolved["octree_resolution"] <= settings.MAX_OCTREE):
        raise HTTPException(
            status_code=422,
            detail=f"octree_resolution must be between {settings.MIN_OCTREE} and {settings.MAX_OCTREE}",
        )
    if resolved["guidance"] <= settings.MIN_GUIDANCE:
        raise HTTPException(status_code=422, detail="guidance must be greater than 0")

    return resolved


def create_app() -> FastAPI:
    settings = get_settings()
    ensure_directories(settings)

    app = FastAPI(title="Hunyuan3D Web Demo")

    # 启用 CORS - 从环境变量读取允许的源，限制HTTP方法
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health() -> JSONResponse:
        return JSONResponse(
            {
                "status": "ok",
                "device": pipeline.get_device(),
                "model_loaded": pipeline.is_model_loaded(),
            }
        )

    @app.post("/api/generate/image")
    async def generate_image(
        file: UploadFile = File(...),
        steps: Optional[int] = Form(default=None),
        guidance: Optional[float] = Form(default=None),
        octree_resolution: Optional[int] = Form(default=None),
        preset: Optional[str] = Form(default=None),
        settings: Settings = Depends(get_settings),
    ) -> JSONResponse:
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image uploads are allowed")

        data = await file.read()
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
        if len(data) > max_bytes:
            raise HTTPException(
                status_code=413, detail=f"File too large (max {settings.MAX_UPLOAD_MB} MB)"
            )

        tmp_name = f"{uuid.uuid4().hex}{Path(file.filename).suffix or '.png'}"
        tmp_path = Path(settings.TMP_DIR) / tmp_name
        with open(tmp_path, "wb") as f:
            f.write(data)

        params = _build_params(preset, steps, guidance, octree_resolution, settings)
        job_id = jobs.create_job(str(tmp_path), params)
        return JSONResponse(
            {
                "job_id": job_id,
                "status_url": f"/api/jobs/{job_id}",
                "result_url": f"/api/jobs/{job_id}/result",
            }
        )

    @app.get("/api/jobs/{job_id}")
    async def get_job(job_id: str):
        job = jobs.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job = dict(job)
        job.pop("input_path", None)
        return JSONResponse(job)

    @app.get("/api/jobs/{job_id}/result")
    async def get_job_result(job_id: str):
        job = jobs.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job["state"] != jobs.JobState.SUCCEEDED:
            raise HTTPException(status_code=409, detail=f"Job not ready: {job['state']}")
        out_path = job.get("out_path")
        if not out_path or not os.path.exists(out_path):
            raise HTTPException(status_code=404, detail="Result not found")
        return FileResponse(
            out_path,
            media_type="model/gltf-binary",
            filename=os.path.basename(out_path),
        )

    @app.delete("/api/jobs/{job_id}")
    async def delete_job(job_id: str):
        job = jobs.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        deleted = jobs.delete_job(job_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete job")
        return JSONResponse({"deleted": True})

    # 允许的模型文件扩展名
    ALLOWED_MODEL_EXTENSIONS = {'.gltf', '.glb', '.bin'}

    def _validate_model_filename(filename: str) -> bool:
        """验证模型文件名是否合法"""
        if not filename:
            return False
        
        # 文件名白名单验证：只允许字母、数字、下划线、连字符和点号
        import re
        if not re.match(r'^[\w\-\.]+$', filename):
            return False
        
        # 验证文件扩展名
        if not any(filename.lower().endswith(ext) for ext in ALLOWED_MODEL_EXTENSIONS):
            return False
        
        return True

    def _generate_model_url(model_path: str) -> str:
        """从模型路径生成可访问的URL"""
        if not model_path:
            return ""
        
        # 使用os.path.basename()提取文件名，支持跨平台
        model_filename = os.path.basename(model_path)
        
        # 验证文件名合法性
        if not _validate_model_filename(model_filename):
            logger.warning(f"Invalid model_path: {model_path}")
            return ""
        
        return f"/api/models/{model_filename}"

    # 历史记录相关 API
    @app.get("/api/history")
    async def get_history(limit: int = 10):
        """获取历史记录列表"""
        history = get_db().get_history(limit)
        # 转换模型路径为可访问的 URL
        for item in history:
            if item.get('model_path'):
                item['model_url'] = _generate_model_url(item['model_path'])
        return JSONResponse(history)

    @app.post("/api/history")
    async def add_history(
        filename: str = Form(...),
        model_path: str = Form(...),
        preset: Optional[str] = Form(None),
        steps: Optional[int] = Form(None),
        guidance: Optional[float] = Form(None),
        octree_resolution: Optional[int] = Form(None),
        settings: Settings = Depends(get_settings)
    ):
        """添加历史记录"""
        import uuid
        from datetime import datetime
        
        # 验证filename参数 - 防止路径遍历攻击
        if not filename:
            raise HTTPException(status_code=400, detail="Invalid filename: empty")
        
        try:
            filename_path = Path(filename)
            # 检查是否为绝对路径或包含路径分隔符
            if filename_path.is_absolute() or filename_path.parts != (filename,):
                raise HTTPException(status_code=400, detail="Invalid filename: path separators not allowed")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid filename format")
        
        # 验证model_path参数 - 确保路径在允许的输出目录内
        try:
            output_dir = Path(settings.OUTPUT_DIR).resolve()
            model_path_obj = Path(model_path)
            # 如果提供的是相对路径，转换为绝对路径
            if not model_path_obj.is_absolute():
                model_path_obj = (output_dir / model_path).resolve()
            else:
                model_path_obj = model_path_obj.resolve()
            
            # 确保路径在输出目录内
            try:
                model_path_obj.relative_to(output_dir)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid model_path: path must be within output directory")
            
            # 验证文件类型
            if model_path_obj.suffix.lower() not in ALLOWED_MODEL_EXTENSIONS:
                raise HTTPException(status_code=400, detail="Invalid file type")
                
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid model_path format")
        
        history_data = {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "model_path": model_path,
            "timestamp": datetime.now().isoformat(),
            "preset": preset,
            "steps": steps,
            "guidance": guidance,
            "octree_resolution": octree_resolution
        }
        
        success = get_db().add_history(history_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add history")
        
        # 转换模型路径为可访问的 URL
        history_data['model_url'] = _generate_model_url(model_path)
        
        return JSONResponse(history_data)

    @app.delete("/api/history/{history_id}")
    async def delete_history(history_id: str):
        """删除历史记录"""
        success = get_db().delete_history(history_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete history")
        return JSONResponse({"deleted": True})

    @app.get("/api/models/{filename}")
    async def get_model(filename: str, settings: Settings = Depends(get_settings)):
        """获取模型文件"""
        # 使用pathlib.Path进行严格的路径验证
        # 首先验证文件名基本格式（防止URL编码或Unicode字符攻击）
        try:
            # 尝试将文件名作为纯路径组件处理
            filename_path = Path(filename)
            # 检查文件名是否包含路径分隔符或父目录引用
            if filename_path.parts != (filename,):
                raise HTTPException(status_code=400, detail="Invalid filename: path separators not allowed")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid filename format")
        
        # 文件类型白名单验证
        allowed_extensions = {'.gltf', '.glb', '.bin'}
        ext = Path(filename).suffix.lower()
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # 构造安全的路径 - 使用resolve()进行严格的路径解析
        output_dir = Path(settings.OUTPUT_DIR).resolve()
        try:
            model_path = (output_dir / filename).resolve(strict=False)
        except (OSError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid path")
        
        # 确保路径在输出目录内（使用resolve()后的严格验证）
        try:
            model_path.relative_to(output_dir)
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # 限制文件大小（100MB）
        max_file_size = 100 * 1024 * 1024
        if model_path.stat().st_size > max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        return FileResponse(
            model_path,
            media_type="model/gltf-binary",
            filename=filename
        )

    static_dir = Path(__file__).resolve().parent.parent / "static"
    app.mount(
        "/",
        StaticFiles(directory=static_dir, html=True),
        name="static",
    )

    @app.get("/")
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/index.html")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("web_demo.backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
