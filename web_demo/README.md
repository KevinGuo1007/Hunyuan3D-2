# Web Demo（FastAPI + model-viewer）

此目录是 Fork 版本新增的 Web 交互模块，用于将图片上传、3D 生成、在线预览整合为单页应用。

## 目录说明

- `backend/app/main.py`：FastAPI 入口与路由
- `backend/app/jobs.py`：任务队列与状态管理
- `backend/app/pipeline.py`：模型加载与推理调用
- `backend/static/`：前端页面与样式脚本
- `backend/web/`：Nuxt.js 前端项目
- `outputs/`：生成结果目录（已在 `.gitignore`）
- `tmp/`：上传缓存目录（已在 `.gitignore`）

## 启动方式

请优先参考仓库根目录 `README.md` 的完整安装流程。安装依赖后运行：

```bash
uvicorn web_demo.backend.app.main:app --host 0.0.0.0 --port 8000
```

打开 `http://127.0.0.1:8000` 即可使用。

## 环境变量

Web Demo 支持通过环境变量配置模型与运行参数，详见根目录 `README.md` 的「可配置环境变量」章节。
