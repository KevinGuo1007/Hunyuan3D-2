import { ref, nextTick } from 'vue'

export const useModelGeneration = (addToHistoryCallback = null) => {
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

  const handleGLBFileChange = (event) => {
    const file = event.target.files && event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const arrayBuffer = e.target.result
        modelUrl.value = arrayBuffer
        downloadLink.value = URL.createObjectURL(file)
        viewerPlaceholder.value = ''
        setStatus('GLB file uploaded. Ready to view.')
        appendLog(`Uploaded GLB file: ${file.name}`)
        
        // 本地上传的 GLB 文件不添加到历史记录
        // 因为这些文件只存在于浏览器中，没有保存到服务器
      }
      reader.onerror = () => {
        setStatus('Failed to read GLB file', true)
        appendLog('Error reading GLB file')
      }
      reader.readAsArrayBuffer(file)
    }
  }

  const startGeneration = async (addToHistoryCallback) => {
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
      pollJob(data.job_id, data.status_url, data.result_url, addToHistoryCallback)
    } catch (err) {
      console.error(err)
      setStatus(err.message || 'Failed to start generation', true)
      appendLog(`Error starting job: ${err.message || err}`)
      isGenerating.value = false
    }
  }

  const pollJob = async (jobId, statusUrl, resultUrl, addToHistoryCallback) => {
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
          
          // 获取文件名
          const fileInput = document.getElementById('file-input')
          const filename = fileInput.files && fileInput.files[0] ? fileInput.files[0].name : 'generated_model'
          
          // 添加到历史记录
          if (addToHistoryCallback) {
            addToHistoryCallback(filename, resultUrl)
          }
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

  const generate3DModel = (addToHistoryCallback) => {
    if (!previewImage.value) {
      setStatus('Please upload an image first', true)
      appendLog('No image selected')
      return
    }

    isGenerating.value = true
    resetUI({keepPreview: true})
    startGeneration(addToHistoryCallback)
  }

  return {
    previewImage,
    preset,
    statusText,
    statusColor,
    progress,
    paramReadout,
    downloadLink,
    modelUrl,
    viewerPlaceholder,
    logOutput,
    isGenerating,
    setStatus,
    appendLog,
    handleFileChange,
    handleGLBFileChange,
    generate3DModel
  }
}