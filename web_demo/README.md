# Hunyuan3D Web Demo

FastAPI + `<model-viewer>` demo for turning images into GLB meshes via Hunyuan3D-2.

## Prerequisites
- Python 3.9+
- PyTorch (with MPS/CPU support). Install matching build for your platform.
- Model weights placed in `./models` and environment variable `HY3DGEN_MODELS` pointing to that folder.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .  # installs hy3dgen package from this repo
pip install fastapi uvicorn pydantic pillow
```

## Run
```bash
export HY3DGEN_MODELS=./models
uvicorn web_demo.backend.app.main:app --host 0.0.0.0 --port 8000
# Then open http://localhost:8000
```

Outputs are saved to `web_demo/outputs`, uploads cached under `web_demo/tmp`.
