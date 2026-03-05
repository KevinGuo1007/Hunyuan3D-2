<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <section class="rounded-lg p-6 shadow-lg flex flex-col gap-5">
      <div class="mb-2">
        <div>
          <p class="text-blue-600 font-semibold text-xs uppercase tracking-wider mb-2">3D Model Assets Generation</p>
          <h1 class="text-2xl font-bold mb-2">Image to 3D Mesh Demo</h1>
          <p class="text-sm text-gray-500">Upload an image, let the model build a 3D shape, then view or download the
            GLB.</p>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <label class="font-semibold text-gray-500 text-sm" for="file-input">Choose an image</label>
        <input class="text-white" id="file-input" accept="image/*"  type="file" @change="handleFileChange"/>
      </div>

      <div class="rounded overflow-hidden text-gray-500">
        <div class="px-4 py-3 font-semibold  ">
          <span>Preview</span>
        </div>
        <div class="p-4 min-h-[200px] flex items-center justify-center">
          <img v-if="previewImage" id="preview-image" :src="previewImage" alt="Preview"
               class="max-w-full max-h-[300px] rounded"/>
          <div v-else id="preview-placeholder">No image selected</div>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <label class="font-semibold text-gray-900 text-sm" for="preset-select">Preset</label>
<!--        <div class="flex gap-4 text-white">-->
<!--          <label-->
<!--              class="flex items-center gap-1 px-3 py-2 rounded cursor-pointer transition-all border- border-transparent hover:border-blue-600 hover:bg-blue-50">-->
<!--            <input id="preset-speed" v-model="preset" name="preset" type="radio" value="speed"/>-->
<!--            <span>速度优先</span>-->
<!--          </label>-->
<!--          <label-->
<!--              class="flex items-center gap-1 px-3 py-2 rounded cursor-pointer transition-all border border-transparent hover:border-blue-600 hover:bg-blue-50">-->
<!--            <input id="preset-quality" v-model="preset" name="preset" type="radio" value="quality"/>-->
<!--            <span>质量优先</span>-->
<!--          </label>-->
<!--        </div>-->
        <a-radio-group class="rounded-lg" >
          <a-radio value="A" class="text-gray-500" >速度优先</a-radio>
          <a-radio value="B">质量优先</a-radio>
        </a-radio-group>
      </div>

      <div class="flex items-center gap-4 mt-2">
        <button id="generate-btn" :disabled="isGenerating || !previewImage"
                class="bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-[#0b1020] border-0 px-[18px] py-[12px] rounded-[12px] font-bold cursor-pointer transition ease-in-out duration-200 shadow-[0_10px_30px_rgba(56,189,248,0.35)] hover:opacity-90 hover:scale-105" type="button"
                @click="generate3DModel">
          {{ isGenerating ? 'Generating...' : 'Generate' }}
        </button>
        <span id="status-text" :style="{ color: statusColor }" class="text-sm">{{ statusText }}</span>
      </div>

      <div class="h-2 overflow-hidden mt-2">
        <div id="progress-bar" :style="{ width: (progress * 100) + '%' }"
             class="h-full bg-blue-600 rounded transition-all duration-300"></div>
      </div>

      <div class="mt-2 text-sm text-gray-500">
        <span id="param-readout">{{ paramReadout }}</span>
      </div>

      <div class="mt-4 flex justify-center">
        <a v-if="downloadLink" id="download-link" :href="downloadLink"
           class="bg-green-600 px-6 py-3 rounded text-sm font-semibold no-underline transition-all hover:bg-green-700"
           download>Download
          GLB</a>
      </div>
    </section>

    <section id="viewer-section" class="rounded-lg p-6 shadow-lg flex items-center justify-center min-h-[480px]">
      <div v-if="!modelUrl" id="viewer-placeholder" class="text-center text-gray-400">{{ viewerPlaceholder }}</div>
      <model-viewer
          v-if="modelUrl"
          id="viewer"
          :src="modelUrl"
          ar
          auto-rotate
          camera-controls
          exposure="1"
          shadow-intensity="0"
          style="width: 100%; height: 480px"
          @load="onViewerLoad"
      >
      </model-viewer>
    </section>

    <section class="rounded-lg p-6 shadow-lg col-span-1 md:col-span-2">
      <div class="mb-2">
        <h2 class="text-xl font-bold">Inference Logs</h2>
        <p class="text-sm text-gray-500">Realtime info from the current session</p>
      </div>
      <div class="h-[300px] overflow-y-auto rounded p-3 mt-3 bg-gray-50">
        <pre class="m-0 font-mono text-sm leading-relaxed text-gray-900 whitespace-pre-wrap break-words">{{
            logOutput
          }}</pre>
      </div>
    </section>
  </div>
</template>

<script setup>
const previewImage = ref('')
const preset = ref('speed')
const statusText = ref('Waiting for upload')
const statusColor = ref('#86909c')
const progress = ref(0)
const paramReadout = ref('Params: -')
const downloadLink = ref('')
const modelUrl = ref('')
const viewerPlaceholder = ref('Welcome to Hunyuan3D! No mesh yet.')
const logOutput = ref('Waiting for activity…')
const isGenerating = ref(false)
let pollTimer = null

const handleFileChange = (event) => {
  const file = event.target.files && event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target.result
      setStatus('Image uploaded. Ready to generate.')
      appendLog(`Selected file: ${file.name}`)
    }
    reader.readAsDataURL(file)
  } else {
    resetUI()
  }
}

const setStatus = (text, isError = false) => {
  statusText.value = text
  statusColor.value = isError ? '#f87171' : '#86909c'
}

const setProgress = (value) => {
  progress.value = Math.min(Math.max(value, 0), 1)
}

const resetUI = (opts = {}) => {
  const {keepPreview = false} = opts
  setProgress(0)
  setStatus('Waiting for upload')
  downloadLink.value = ''
  modelUrl.value = ''
  viewerPlaceholder.value = 'Welcome to Hunyuan3D! No mesh yet.'
  paramReadout.value = 'Params: -'
  if (!keepPreview) {
    previewImage.value = ''
  }
}

const appendLog = (message) => {
  const ts = new Date().toLocaleTimeString()
  const line = `[${ts}] ${message}`
  const current = logOutput.value === 'Waiting for activity…' ? '' : logOutput.value + '\n'
  logOutput.value = current + line

  nextTick(() => {
    const logBox = document.getElementById('log-box')
    if (logBox) {
      logBox.scrollTop = logBox.scrollHeight
    }
  })
}

const renderParams = (params) => {
  if (!params) return
  const {preset: p, steps, guidance, octree_resolution} = params
  paramReadout.value = `Params: preset=${p || '-'} | steps=${steps} | guidance=${guidance} | octree=${octree_resolution}`
}

const onViewerLoad = () => {
  viewerPlaceholder.value = ''
}

const generate3DModel = () => {
  if (!previewImage.value) {
    setStatus('Please upload an image first', true)
    appendLog('No image selected')
    return
  }

  isGenerating.value = true
  resetUI({keepPreview: true})
  startGeneration()
}

const startGeneration = async () => {
  const fileInput = document.getElementById('file-input')
  if (!fileInput.files || !fileInput.files[0]) {
    setStatus('Please choose an image first', true)
    appendLog('No image selected')
    return
  }

  setStatus('Uploading...')
  setProgress(0.05)
  appendLog('Uploading image and starting job…')
  viewerPlaceholder.value = 'Generating… please wait.'

  const form = new FormData()
  form.append('file', fileInput.files[0])
  form.append('preset', preset.value)

  try {
    const resp = await fetch('/api/generate/image', {method: 'POST', body: form})
    if (!resp.ok) {
      const msg = await resp.text()
      throw new Error(msg || 'Failed to start job')
    }
    const data = await resp.json()
    setStatus('Queued')
    setProgress(0.1)
    appendLog(`Job queued: ${data.job_id}`)
    pollJob(data.job_id, data.status_url, data.result_url)
  } catch (err) {
    console.error(err)
    setStatus(err.message || 'Failed to start generation', true)
    appendLog(`Error starting job: ${err.message || err}`)
    isGenerating.value = false
  }
}

const pollJob = async (jobId, statusUrl, resultUrl) => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }

  pollTimer = setInterval(async () => {
    try {
      const resp = await fetch(statusUrl)
      if (!resp.ok) {
        throw new Error('Failed to fetch job status')
      }
      const job = await resp.json()
      setStatus(`${job.state}...`)
      renderParams(job.params)

      if (typeof job.progress === 'number') {
        setProgress(job.progress)
      }

      if (job.logs) {
        logOutput.value = job.logs
        nextTick(() => {
          const logBox = document.getElementById('log-box')
          if (logBox) {
            logBox.scrollTop = logBox.scrollHeight
          }
        })
      }

      if (job.state !== 'succeeded' && job.state !== 'failed') {
        appendLog(`Job ${job.job_id} is ${job.state}`)
      }

      if (job.state === 'succeeded') {
        clearInterval(pollTimer)
        pollTimer = null
        modelUrl.value = resultUrl
        downloadLink.value = resultUrl
        setStatus('Done')
        setProgress(1)
        isGenerating.value = false
        appendLog(`Job ${job.job_id} succeeded. Result ready.`)
      } else if (job.state === 'failed') {
        clearInterval(pollTimer)
        pollTimer = null
        setStatus(job.error || 'Job failed', true)
        isGenerating.value = false
        appendLog(`Job ${job.job_id} failed: ${job.error || 'Unknown error'}`)
        viewerPlaceholder.value = job.error || 'Job failed'
      }
    } catch (err) {
      console.error(err)
      clearInterval(pollTimer)
      pollTimer = null
      setStatus(err.message || 'Error polling job', true)
      isGenerating.value = false
      appendLog(`Polling error: ${err.message || err}`)
    }
  }, 1000)
}
</script>
