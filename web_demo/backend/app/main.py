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

    if os.getenv("ENABLE_CORS", "").lower() in {"1", "true", "yes"}:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
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
