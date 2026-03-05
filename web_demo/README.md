# Web Demo（FastAPI + model-viewer）

此目录是 Fork 版本新增的 Web 交互模块，用于将图片上传、3D 生成、在线预览整合为单页应用。

## 目录说明

### 后端模块
- `backend/app/main.py`：FastAPI 入口与路由
- `backend/app/jobs.py`：任务队列与状态管理
- `backend/app/pipeline.py`：模型加载与推理调用
- `backend/app/settings.py`：应用配置

### 前端模块
- `backend/nuxt/`：Nuxt.js 前端框架目录
- `backend/static/`：前端构建输出目录

### 存储目录
- `outputs/`：生成结果目录（已在 `.gitignore`）
- `tmp/`：上传缓存目录（已在 `.gitignore`）

## 启动方式

请优先参考仓库根目录 `README.md` 的完整安装流程。

### 1. 安装依赖

```bash
# 安装前端依赖（在 nuxt 目录）
cd web_demo/backend/nuxt
npm install
```
### 2. 构建前端

```bash
cd web_demo/backend/nuxt
npm run build
```

### 3. 启动后端

```bash
cd ../../..
uvicorn web_demo.backend.app.main:app 
```

打开 `http://127.0.0.1:8000` 即可使用。

## 环境变量

Web Demo 支持通过环境变量配置模型与运行参数，详见根目录 `README.md` 的「可配置环境变量」章节。
