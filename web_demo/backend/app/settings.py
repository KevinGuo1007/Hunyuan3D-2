import os
from dataclasses import dataclass
from functools import lru_cache


def _get_env(key: str, default, cast_type):
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return cast_type(value)
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    MODEL_REPO: str
    MODEL_SUBFOLDER: str
    OUTPUT_DIR: str
    TMP_DIR: str
    MAX_UPLOAD_MB: int
    MAX_CONCURRENCY: int
    DEFAULT_STEPS: int
    DEFAULT_GUIDANCE: float
    DEFAULT_OCTREE_RESOLUTION: int
    PRESETS: dict
    DEFAULT_PRESET: str
    ALLOWED_ORIGINS: list
    MIN_STEPS: int = 1
    MAX_STEPS: int = 100
    MIN_OCTREE: int = 16
    MAX_OCTREE: int = 512
    MIN_GUIDANCE: float = 0.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    presets = {
        "speed": {"steps": 10, "guidance": 5.0, "octree": 192},
        "quality": {"steps": 30, "guidance": 5.0, "octree": 384},
    }
    # 从环境变量读取允许的CORS源，生产环境必须配置特定域名
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    
    # 如果未配置，使用默认开发环境地址
    if not allowed_origins:
        allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    return Settings(
        MODEL_REPO=os.getenv("MODEL_REPO", "tencent/Hunyuan3D-2mini"),
        MODEL_SUBFOLDER=os.getenv("MODEL_SUBFOLDER", "hunyuan3d-dit-v2-mini"),
        OUTPUT_DIR=os.getenv("OUTPUT_DIR", "web_demo/outputs"),
        TMP_DIR=os.getenv("TMP_DIR", "web_demo/tmp"),
        MAX_UPLOAD_MB=_get_env("MAX_UPLOAD_MB", 10, int),
        MAX_CONCURRENCY=_get_env("MAX_CONCURRENCY", 1, int),
        DEFAULT_STEPS=_get_env("DEFAULT_STEPS", 10, int),
        DEFAULT_GUIDANCE=_get_env("DEFAULT_GUIDANCE", 5.0, float),
        DEFAULT_OCTREE_RESOLUTION=_get_env("DEFAULT_OCTREE_RESOLUTION", 192, int),
        PRESETS=presets,
        DEFAULT_PRESET=os.getenv("DEFAULT_PRESET", "speed"),
        ALLOWED_ORIGINS=allowed_origins,
    )
