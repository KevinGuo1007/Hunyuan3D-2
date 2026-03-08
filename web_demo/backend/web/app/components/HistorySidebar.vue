<template>
  <div :class="['transition-all duration-300 ease-in-out', sidebarExpanded ? 'md:w-64 lg:w-72' : 'md:w-12']" class="flex-shrink-0">
    <div class="bg-gray-900 rounded-lg shadow-lg h-full flex flex-col">
      <!-- 侧边栏头部 -->
      <div class="p-4 border-b border-gray-800 flex items-center">
        <h2 v-if="sidebarExpanded" class="text-lg font-bold text-white mr-4">History</h2>
        <button 
          @click="toggleSidebar" 
          class="text-gray-400 hover:text-white transition-colors ml-auto"
        >
          <svg v-if="sidebarExpanded" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </div>
      
      <!-- 历史记录列表 -->
      <div v-if="sidebarExpanded" class="flex-1 overflow-y-auto p-4">
        <div v-if="history.length === 0" class="text-center text-gray-500 py-8">
          No history yet
        </div>
        <div v-else class="space-y-3">
          <div 
            v-for="(item, index) in history" 
            :key="item.id"
            class="bg-gray-800 rounded-lg p-3 hover:bg-gray-700 transition-colors"
          >
            <div class="flex items-center gap-3 cursor-pointer" @click="loadHistoryItem(item)">
              <div class="w-12 h-12 rounded bg-gray-700 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-400">
                  <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
                  <polyline points="7.5 4.21 12 6.81 16.5 4.21"/>
                  <polyline points="7.5 19.79 7.5 14.6 3 12"/>
                  <polyline points="21 12 16.5 14.6 16.5 19.79"/>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                  <line x1="12" x2="12" y1="22.08" y2="12"/>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-white truncate">{{ item.filename }}</p>
                <p class="text-xs text-gray-400">{{ formatDate(item.timestamp) }}</p>
              </div>
            </div>
            <div class="mt-2 flex gap-2">
              <button 
                @click.stop="loadHistoryItem(item)"
                class="text-xs px-2 py-1 bg-blue-600 rounded hover:bg-blue-700 transition-colors"
              >
                View
              </button>
              <button 
                @click.stop="downloadModel(item)"
                class="text-xs px-2 py-1 bg-green-600 rounded hover:bg-green-700 transition-colors"
              >
                Download
              </button>
              <button 
                @click.stop="deleteHistoryItem(item.id)"
                class="text-xs px-2 py-1 bg-red-600 rounded hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  sidebarExpanded: {
    type: Boolean,
    default: true
  },
  history: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'toggleSidebar',
  'loadHistoryItem',
  'downloadModel',
  'deleteHistoryItem'
])

const toggleSidebar = () => {
  emit('toggleSidebar')
}

const loadHistoryItem = (item) => {
  emit('loadHistoryItem', item)
}

const downloadModel = (item) => {
  emit('downloadModel', item)
}

const deleteHistoryItem = (id) => {
  emit('deleteHistoryItem', id)
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}
</script>