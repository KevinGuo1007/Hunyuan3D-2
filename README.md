# Hunyuan3D-2 Web Studio（Fork 版本）

本仓库基于腾讯开源项目 [Tencent-Hunyuan/Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) 二次开发。  
在保留原始 `hy3dgen` 推理能力的基础上，新增了一个可直接使用的 Web 端工作流，把 **上传图片 → 生成 3D 模型 → 在线预览与下载** 串成一个完整流程。

---

## 1. Fork 版本做了什么

- 新增 `web_demo`：FastAPI 后端 + 纯前端静态页面（`<model-viewer>`）。
- 支持单图生成 GLB，支持任务排队、进度查询和日志回显。
- 提供速度/质量两个预设参数（`speed` / `quality`）。
- 保留原仓库脚本能力（`minimal_demo.py`、`gradio_app.py`、`api_server.py` 等）。

---

## 2. 项目结构（整理后建议认知）

```text
.
├── hy3dgen/                    # 核心推理包（上游主代码）
├── web_demo/                   # 你新增的 Web Demo
│   ├── backend/app/            # FastAPI 业务逻辑（接口、任务、推理）
│   ├── backend/static/         # 前端页面（上传、进度、3D 预览）
│   ├── outputs/                # 生成结果目录（已加入 .gitignore）
│   └── tmp/                    # 上传临时目录（已加入 .gitignore）
├── examples/                   # 上游示例脚本
├── assets/                     # 示例资源
├── requirements.txt
├── setup.py
└── README.md                   # 当前文档（Fork 版本说明）
```

---

## 3. 环境要求

- Python 3.9+（推荐 3.10/3.11）
- PyTorch（按你的设备安装：CPU / CUDA / MPS）
- 操作系统：macOS / Linux / Windows（Windows 需自行调整命令）
- 建议：16GB+ 内存；有 GPU 时体验更好

---

## 4. 安装与启动

### 4.1 克隆仓库

```bash
git clone https://github.com/KevinGuo1007/Hunyuan3D-2.git
cd Hunyuan3D-2
```

### 4.2 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

> 如果你后续要使用纹理相关能力（非本 Web Demo 必需），再额外编译：
>
> ```bash
> cd hy3dgen/texgen/custom_rasterizer && python setup.py install
> cd ../differentiable_renderer && python setup.py install
> cd ../../..
> ```

### 4.3 启动 Web Demo

```bash
uvicorn web_demo.backend.app.main:app --host 0.0.0.0 --port 8000
```

浏览器打开：

- 本机访问：`http://127.0.0.1:8000`
- 局域网访问：`http://<你的机器IP>:8000`

### 4.4 使用流程

1. 选择一张输入图片（支持透明背景图）。
2. 选择预设：
   - `speed`：更快，默认 `steps=10, octree=192`
   - `quality`：质量更高，默认 `steps=30, octree=384`
3. 点击 `Generate`。
4. 等待任务完成后在线预览并下载 GLB。

---

## 5. Web API 一览

- `GET /api/health`：服务健康状态、运行设备、模型是否已加载
- `POST /api/generate/image`：提交图片生成任务
- `GET /api/jobs/{job_id}`：查询任务状态、参数、日志、进度
- `GET /api/jobs/{job_id}/result`：下载生成结果（GLB）
- `DELETE /api/jobs/{job_id}`：删除任务记录及结果文件

---

## 6. 可配置环境变量（Web Demo）

| 变量名 | 默认值 | 说明 |
| --- | --- | --- |
| `MODEL_REPO` | `tencent/Hunyuan3D-2mini` | Hugging Face 模型仓库 |
| `MODEL_SUBFOLDER` | `hunyuan3d-dit-v2-mini` | 模型子目录 |
| `OUTPUT_DIR` | `web_demo/outputs` | GLB 输出目录 |
| `TMP_DIR` | `web_demo/tmp` | 上传临时目录 |
| `MAX_UPLOAD_MB` | `10` | 上传大小限制（MB） |
| `MAX_CONCURRENCY` | `1` | 后台并发任务数 |
| `DEFAULT_PRESET` | `speed` | 默认预设（`speed`/`quality`） |
| `ENABLE_CORS` | 空 | 设为 `true/1/yes` 时开启跨域 |

示例：

```bash
export MODEL_REPO=tencent/Hunyuan3D-2
export MODEL_SUBFOLDER=hunyuan3d-dit-v2-0
export MAX_CONCURRENCY=2
uvicorn web_demo.backend.app.main:app --host 0.0.0.0 --port 8000
```

---

## 7. Git 管理建议（Fork 同步）

当前仓库已配置：

- `origin`：你的 fork（`KevinGuo1007/Hunyuan3D-2`）
- `upstream`：腾讯原仓库（`Tencent-Hunyuan/Hunyuan3D-2`）

推荐日常流程：

```bash
# 同步上游到本地 main
git checkout main
git fetch upstream
git merge upstream/main
git push origin main

# 新功能用独立分支
git checkout -b feature/<your-feature>
```

建议将 `main` 作为稳定分支，功能开发放在 `feature/*` 分支，完成后再合并回 `main`。

---

## 8. 已加入 .gitignore 的本地/生成文件

为避免仓库变乱，已忽略以下常见本地产物：

- 本地虚拟环境：`hy3d-venv/`
- 生成结果：`out.glb`、`web_demo/outputs/`
- 临时上传：`web_demo/tmp/`
- 本地测试脚本与草稿：`test.py`、`web-demo设计文档.md`
- 本地设计文档：`web_demo/报告文档.md`、`web_demo/*.puml`
- 本地测试图片：`assets/demo_notrans*.png`

---

## 9. 常见问题

- **首次启动较慢**：模型会在首次推理时加载/下载，属于正常现象。
- **Mac 设备**：默认优先使用 MPS（若可用），否则退回 CPU。
- **任务失败**：可先查看页面日志，再检查 `MODEL_REPO` / `MODEL_SUBFOLDER` 是否匹配。

---

## 10. 相关文档

- 上游中文说明：`README_zh_cn.md`
- 上游日文说明：`README_ja_jp.md`
- Web Demo 子文档：`web_demo/README.md`

---

## 11. 许可证

本项目继承上游许可证与使用条款，详见 `LICENSE` 与 `NOTICE`。  
使用模型与代码前，请务必确认用途符合上游许可要求（尤其是商用限制条款）。
