<template>
  <div class="flex flex-col md:flex-row h-screen w-full">
    <!-- 左侧历史记录侧边栏 -->
    <HistorySidebar 
      :sidebarExpanded="sidebarExpanded"
      :history="history"
      @toggleSidebar="toggleSidebar"
      @loadHistoryItem="loadHistoryItem"
      @downloadModel="downloadModel"
      @deleteHistoryItem="deleteHistoryItem"
    />

    <!-- 主内容区域 -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <section class="rounded-lg p-6 shadow-lg flex flex-col gap-5">
        <div class="mb-2">
          <div>
            <p class="text-blue-600 font-semibold text-xs uppercase tracking-wider mb-2">3D Model Assets Generation</p>
            <h1 class="text-2xl font-bold mb-2 text-white">Image to 3D Mesh Demo</h1>
            <p class="text-sm text-gray-500">Upload an image, let the model build a 3D shape, then view or download the
              GLB.</p>
          </div>
        </div>

        <div class="flex flex-col gap-2">
        <label class="font-semibold text-gray-500 text-sm" for="file-input">Choose an image</label>
        <input class="text-white" id="file-input" accept="image/*"  type="file" @change="handleFileChange"/>
      </div>

      <div class="flex flex-col gap-2 mt-4">
        <label class="font-semibold text-gray-500 text-sm" for="glb-input">Upload GLB file (for testing)</label>
        <input class="text-white" id="glb-input" accept=".glb"  type="file" @change="handleGLBFileChange"/>
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

        <div class="flex flex-col gap-2 text-indigo-200">
          <label class="font-semibold text-sm" for="preset-select">Preset</label>
          <div class="flex gap-4 text-white">
            <label
                class="flex items-center gap-1 px-3 py-2 rounded-2xl cursor-pointer transition-all border border-transparent hover:border-blue-600">
              <input id="preset-speed" v-model="preset" name="preset" type="radio" value="speed"/>
              <span>速度优先</span>
            </label>
            <label
                class="flex items-center gap-1 px-3 py-2 rounded-2xl cursor-pointer transition-all border border-transparent hover:border-blue-600">
              <input id="preset-quality" v-model="preset" name="preset" type="radio" value="quality"/>
              <span>质量优先</span>
            </label>
          </div>
        </div>

        <div class="flex items-center gap-4 mt-2">
          <button id="generate-btn" :disabled="isGenerating || !previewImage"
                  class="bg-gradient-to-br from-[#38bdf8] to-[#a855f7] text-[#e5e7eb] border-0 px-[18px] py-[12px] rounded-[12px] font-bold cursor-pointer transition ease-in-out duration-200 shadow-[0_10px_30px_rgba(56,189,248,0.35)] hover:opacity-90 hover:scale-105" type="button"
                  @click="generate3DModelWrapper">
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

      <section id="viewer-section" class=" border-indigo-950 border-2 rounded-lg p-6 shadow-lg flex items-center justify-center min-h-[480px]">
        <div v-if="!modelUrl" id="viewer-placeholder" class="text-center text-gray-400">{{ viewerPlaceholder }}</div>
        <div v-else class="w-full h-full relative">
          <ThreeViewer :modelUrl="modelUrl" />
        </div>
      </section>

      <!-- 日志面板 -->
      <LogPanel :logOutput="logOutput" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import HistorySidebar from '../components/HistorySidebar.vue'
import LogPanel from '../components/LogPanel.vue'
import ThreeViewer from '../components/ThreeViewer.vue'
import { useHistory } from '../composables/useHistory'
import { useModelGeneration } from '../composables/useModelGeneration'

// 历史记录相关
const { history, initHistory, addToHistory, deleteHistoryItem } = useHistory()
const sidebarExpanded = ref(true)

// 模型生成相关
const { 
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
} = useModelGeneration(async (filename, modelUrl) => {
  await addToHistory(filename, modelUrl)
  await initHistory()
})

// 切换侧边栏展开/收起
const toggleSidebar = () => {
  sidebarExpanded.value = !sidebarExpanded.value
}

// 加载历史记录项
const loadHistoryItem = (item) => {
  // 检查 item.model_url 的类型
  if (typeof item.model_url === 'string') {
    // 对于 URL，直接使用
    modelUrl.value = item.model_url
    downloadLink.value = item.model_url
    viewerPlaceholder.value = ''
    setStatus('Loaded from history')
    appendLog(`Loaded model: ${item.filename}`)
  } else {
    // 未知类型
    setStatus('Invalid model data. Please re-upload the file.', true)
    appendLog('Invalid model data type')
  }
}

// 下载模型
const downloadModel = (item) => {
  if (typeof item.model_url === 'string') {
    // 对于 URL，直接使用
    const link = document.createElement('a')
    link.href = item.model_url
    link.download = item.filename.replace(/\.[^/.]+$/, '') + '.glb'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    // 未知类型
    setStatus('Invalid model data. Please re-upload the file.', true)
    appendLog('Invalid model data type')
  }
  appendLog(`Downloaded model: ${item.filename}`)
}

// 生成3D模型
const generate3DModelWrapper = async () => {
  await generate3DModel(async (filename, modelUrl) => {
    await addToHistory(filename, modelUrl)
    await initHistory()
  })
}

// 初始化
onMounted(async () => {
  console.log('Initializing history...')
  await initHistory()
  console.log('History initialized:', history.value.length, 'items')
})
</script>