import logging
import os
import threading
import time
from typing import Optional
import sys

import torch
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from PIL import Image

from .settings import get_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.propagate = True

_pipeline_lock = threading.Lock()
_pipeline_instance: Optional[Hunyuan3DDiTFlowMatchingPipeline] = None
_device: Optional[str] = None


def _select_device() -> str:
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():  # type: ignore[attr-defined]
        return "mps"
    return "cpu"


def get_device() -> str:
    if _device is not None:
        return _device
    return _select_device()


def _load_pipeline() -> Hunyuan3DDiTFlowMatchingPipeline:
    global _pipeline_instance, _device
    if _pipeline_instance is not None:
        return _pipeline_instance

    with _pipeline_lock:
        if _pipeline_instance is not None:
            return _pipeline_instance

        settings = get_settings()
        _device = _select_device()
        dtype = torch.float16 if _device == "mps" else torch.float32

        logger.info(
            "Loading Hunyuan3D pipeline from %s (subfolder=%s) on %s with dtype=%s",
            settings.MODEL_REPO,
            settings.MODEL_SUBFOLDER,
            _device,
            dtype,
        )
        start = time.time()
        pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            settings.MODEL_REPO,
            subfolder=settings.MODEL_SUBFOLDER,
            device=_device,
            torch_dtype=dtype,
        )
        _pipeline_instance = pipe
        logger.info("Pipeline loaded in %.2fs", time.time() - start)
        return _pipeline_instance


def is_model_loaded() -> bool:
    return _pipeline_instance is not None


def _prepare_image(image_path: str) -> Image.Image:
    with Image.open(image_path) as img:
        has_alpha = ("A" in img.getbands()) or ("transparency" in img.info)
        if has_alpha:
            img = img.convert("RGBA")
            logger.info("Loaded image with alpha channel, preserving mask. mode=%s", img.mode)
        else:
            img = img.convert("RGB")
            logger.info("Loaded image without alpha channel. mode=%s", img.mode)

        max_side = max(img.size)
        if max_side > 1024:
            scale = 1024 / float(max_side)
            new_size = (int(img.width * scale), int(img.height * scale))
            resample = getattr(Image, "Resampling", Image).LANCZOS
            img = img.resize(new_size, resample)
            logger.info("Resized image to %s for safety", img.size)
        return img


def generate_glb(
    image_path: str,
    out_glb_path: str,
    steps: int,
    guidance: float,
    octree_resolution: int,
) -> str:
    logger.info(
        "Inference params | image=%s steps=%s guidance=%.2f octree_resolution=%s output=%s",
        image_path,
        steps,
        guidance,
        octree_resolution,
        out_glb_path,
    )

    pipe = _load_pipeline()

    image = _prepare_image(image_path)

    start = time.time()
    output = pipe(
        image=image,
        num_inference_steps=steps,
        guidance_scale=guidance,
        output_type="trimesh",
        octree_resolution=octree_resolution,
    )
    # hy3dgen may return a pipeline output object or a simple list; handle both.
    mesh = getattr(output, "mesh", None)
    if mesh is None and isinstance(output, (list, tuple)) and output:
        mesh = output[0]
    if mesh is None:
        raise RuntimeError("Failed to obtain mesh from pipeline output")

    os.makedirs(os.path.dirname(out_glb_path), exist_ok=True)
    mesh.export(out_glb_path)
    logger.info("Generation finished in %.2fs -> %s", time.time() - start, out_glb_path)
    return out_glb_path
