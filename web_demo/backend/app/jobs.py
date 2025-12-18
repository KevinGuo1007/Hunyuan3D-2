import logging
import os
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, Optional
from contextlib import redirect_stdout, redirect_stderr

from .pipeline import generate_glb
from .settings import get_settings

logger = logging.getLogger(__name__)


class JobState:
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobManager:
    def __init__(self) -> None:
        settings = get_settings()
        self.output_dir = settings.OUTPUT_DIR
        self.max_workers = settings.MAX_CONCURRENCY
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_job(self, input_path: str, params: Dict[str, Any]) -> str:
        job_id = uuid.uuid4().hex
        now = datetime.utcnow().isoformat()
        out_path = os.path.join(self.output_dir, f"{job_id}.glb")
        with self._lock:
            self.jobs[job_id] = {
                "job_id": job_id,
                "state": JobState.QUEUED,
                "progress": 0.0,
                "error": None,
                "created_at": now,
                "updated_at": now,
                "out_path": out_path,
                "params": params,
                "input_path": input_path,
                "logs": "",
            }

        future = self.executor.submit(self._run_job, job_id)
        future.add_done_callback(lambda _: None)
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self.jobs.get(job_id)
            if job is None:
                return None
            return dict(job)

    def delete_job(self, job_id: str) -> bool:
        with self._lock:
            job = self.jobs.pop(job_id, None)
        if job is None:
            return False

        out_path = job.get("out_path")
        if out_path and os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                logger.warning("Failed to remove output file: %s", out_path)
        return True

    def _update_job(self, job_id: str, **updates: Any) -> None:
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                return
            job.update(updates)
            job["updated_at"] = datetime.utcnow().isoformat()

    def _append_log(self, job_id: str, text: str) -> None:
        if not text:
            return
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                return
            logs = job.get("logs") or ""
            # Trim to avoid unbounded memory; keep last ~20000 chars
            combined = (logs + text)[-20000:]
            job["logs"] = combined
            job["updated_at"] = datetime.utcnow().isoformat()

    def _run_job(self, job_id: str) -> None:
        job = self.get_job(job_id)
        if not job:
            return

        params = job["params"]
        input_path = job["input_path"]
        out_path = job["out_path"]

        self._update_job(job_id, state=JobState.RUNNING, progress=0.1)
        try:
            log_writer_out = _JobLogWriter(job_id, self, base_stream=sys.__stdout__)
            log_writer_err = _JobLogWriter(job_id, self, base_stream=sys.__stderr__)
            with redirect_stdout(log_writer_out), redirect_stderr(log_writer_err):
                generate_glb(
                    image_path=input_path,
                    out_glb_path=out_path,
                    steps=params["steps"],
                    guidance=params["guidance"],
                    octree_resolution=params["octree_resolution"],
                )
            self._update_job(job_id, progress=0.9)
            self._update_job(job_id, state=JobState.SUCCEEDED, progress=1.0)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Job %s failed", job_id)
            self._update_job(
                job_id,
                state=JobState.FAILED,
                error=str(exc),
                progress=1.0,
            )
        finally:
            if os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except OSError:
                    logger.warning("Failed to remove temp input: %s", input_path)


manager = JobManager()


def create_job(input_path: str, params: Dict[str, Any]) -> str:
    return manager.create_job(input_path, params)


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    return manager.get_job(job_id)


def delete_job(job_id: str) -> bool:
    return manager.delete_job(job_id)


class _JobLogWriter:
    def __init__(self, job_id: str, mgr: JobManager, base_stream=sys.__stdout__) -> None:
        self.job_id = job_id
        self.mgr = mgr
        self.base_stream = base_stream

    def write(self, text: str) -> int:  # type: ignore[override]
        if not text:
            return 0
        # Mirror to original stream so terminal still shows progress.
        try:
            self.base_stream.write(text)
            self.base_stream.flush()
        except Exception:
            pass
        # Normalize carriage returns for UI readability.
        normalized = text.replace("\r", "\n")
        self.mgr._append_log(self.job_id, normalized)
        return len(text)

    def flush(self) -> None:  # noqa: D401
        """Flush is a no-op for the in-memory writer."""
        return
