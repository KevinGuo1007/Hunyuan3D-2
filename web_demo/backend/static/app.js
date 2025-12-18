const fileInput = document.querySelector("#file-input");
const generateBtn = document.querySelector("#generate-btn");
const statusText = document.querySelector("#status-text");
const progressBar = document.querySelector("#progress-bar");
const viewerSection = document.querySelector("#viewer-section");
const viewer = document.querySelector("#viewer");
const downloadLink = document.querySelector("#download-link");
const presetInputs = document.querySelectorAll('input[name="preset"]');
const paramReadout = document.querySelector("#param-readout");
const previewImage = document.querySelector("#preview-image");
const previewPlaceholder = document.querySelector("#preview-placeholder");
const viewerPlaceholder = document.querySelector("#viewer-placeholder");
const logOutput = document.querySelector("#log-output");
const logBox = document.querySelector("#log-box");

let pollTimer = null;
let lastJobState = null;

function setStatus(text, isError = false) {
  statusText.textContent = text;
  statusText.style.color = isError ? "#f87171" : "var(--muted)";
}

function setProgress(value) {
  const clamped = Math.min(Math.max(value, 0), 1);
  progressBar.style.width = `${(clamped * 100).toFixed(0)}%`;
}

function resetUI(opts = {}) {
  const { keepPreview = false } = opts;
  setProgress(0);
  setStatus("Waiting for upload");
  viewerSection.hidden = false;
  downloadLink.hidden = true;
  viewer.src = "";
  if (viewerPlaceholder) {
    viewerPlaceholder.textContent = "Welcome to Hunyuan3D! No mesh yet.";
    viewerPlaceholder.hidden = false;
  }
  paramReadout.textContent = "Params: -";
  if (!keepPreview) {
    if (previewImage) {
      previewImage.src = "";
      previewImage.hidden = true;
    }
    if (previewPlaceholder) previewPlaceholder.hidden = false;
  }
  lastJobState = null;
}

function getSelectedPreset() {
  const checked = Array.from(presetInputs).find((el) => el.checked);
  return checked ? checked.value : "speed";
}

function appendLog(message) {
  if (!logOutput) return;
  const ts = new Date().toLocaleTimeString();
  const line = `[${ts}] ${message}`;
  const current = logOutput.textContent === "Waiting for activity…" ? "" : logOutput.textContent + "\n";
  logOutput.textContent = current + line;
  if (logBox) {
    logBox.scrollTop = logBox.scrollHeight;
  }
}

function updatePreview(file) {
  if (!file || !previewImage) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    previewImage.hidden = false;
    if (previewPlaceholder) previewPlaceholder.hidden = true;
  };
  reader.readAsDataURL(file);
}

async function startGeneration() {
  if (!fileInput.files || !fileInput.files[0]) {
    setStatus("Please choose an image first", true);
    appendLog("No image selected");
    return;
  }

  generateBtn.disabled = true;
  setStatus("Uploading...");
  setProgress(0.05);
  appendLog("Uploading image and starting job…");
  if (viewerPlaceholder) {
    viewerPlaceholder.textContent = "Generating… please wait.";
    viewerPlaceholder.hidden = false;
  }

  const form = new FormData();
  form.append("file", fileInput.files[0]);
  form.append("preset", getSelectedPreset());

  try {
    const resp = await fetch("/api/generate/image", { method: "POST", body: form });
    if (!resp.ok) {
      const msg = await resp.text();
      throw new Error(msg || "Failed to start job");
    }
    const data = await resp.json();
    setStatus("Queued");
    setProgress(0.1);
    appendLog(`Job queued: ${data.job_id}`);
    pollJob(data.job_id, data.status_url, data.result_url);
  } catch (err) {
    console.error(err);
    setStatus(err.message || "Failed to start generation", true);
    appendLog(`Error starting job: ${err.message || err}`);
    generateBtn.disabled = false;
  }
}

function renderParams(params) {
  if (!params) return;
  const { preset, steps, guidance, octree_resolution } = params;
  paramReadout.textContent = `Params: preset=${preset || "-"} | steps=${steps} | guidance=${guidance} | octree=${octree_resolution}`;
}

async function pollJob(jobId, statusUrl, resultUrl) {
  if (pollTimer) {
    clearInterval(pollTimer);
  }
  pollTimer = setInterval(async () => {
    try {
      const resp = await fetch(statusUrl);
      if (!resp.ok) {
        throw new Error("Failed to fetch job status");
      }
      const job = await resp.json();
      setStatus(`${job.state}...`);
      renderParams(job.params);
      if (typeof job.progress === "number") {
        setProgress(job.progress);
      }

      if (logOutput && job.logs) {
        logOutput.textContent = job.logs;
        if (logBox) {
          logBox.scrollTop = logBox.scrollHeight;
        }
      }

       if (job.state !== lastJobState) {
         appendLog(`Job ${job.job_id} is ${job.state}`);
         lastJobState = job.state;
       }

      if (job.state === "succeeded") {
        clearInterval(pollTimer);
        pollTimer = null;
        viewer.src = resultUrl;
        if (viewerPlaceholder) viewerPlaceholder.hidden = true;
        downloadLink.href = resultUrl;
        downloadLink.hidden = false;
        setStatus("Done");
        setProgress(1);
        generateBtn.disabled = false;
        appendLog(`Job ${job.job_id} succeeded. Result ready.`);
      } else if (job.state === "failed") {
        clearInterval(pollTimer);
        pollTimer = null;
        setStatus(job.error || "Job failed", true);
        generateBtn.disabled = false;
        appendLog(`Job ${job.job_id} failed: ${job.error || "Unknown error"}`);
        if (viewerPlaceholder) {
          viewerPlaceholder.textContent = job.error || "Job failed";
          viewerPlaceholder.hidden = false;
        }
      }
    } catch (err) {
      console.error(err);
      clearInterval(pollTimer);
      pollTimer = null;
      setStatus(err.message || "Error polling job", true);
      generateBtn.disabled = false;
      appendLog(`Polling error: ${err.message || err}`);
    }
  }, 1000);
}

generateBtn.addEventListener("click", () => {
  resetUI({ keepPreview: true });
  startGeneration();
});

if (viewer) {
  viewer.addEventListener("load", () => {
    if (viewerPlaceholder) {
      viewerPlaceholder.hidden = true;
    }
  });
}

fileInput.addEventListener("change", (e) => {
  const file = e.target.files && e.target.files[0];
  if (file) {
    updatePreview(file);
    appendLog(`Selected file: ${file.name}`);
  } else {
    resetUI();
  }
});

resetUI();
