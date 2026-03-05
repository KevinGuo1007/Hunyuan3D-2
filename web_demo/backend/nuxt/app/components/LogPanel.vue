<template>
  <a-card class="log-panel" :bordered="false">
    <template #title>
      <div class="log-header">
        <icon-file />
        <span>Inference Logs</span>
        <a-tag size="small" :color="logs.length > 0 ? 'arcoblue' : 'gray'">
          {{ logs.length }} 条
        </a-tag>
      </div>
    </template>
    
    <template #extra>
      <a-space>
        <a-button type="primary" size="small" status="danger" @click="clearLogs">
          <template #icon><icon-delete /></template>
          清空
        </a-button>
        <a-button size="small" @click="exportLogs">
          <template #icon><icon-download /></template>
          导出
        </a-button>
      </a-space>
    </template>

    <div ref="logContainerRef" class="log-container">
      <a-empty v-if="logs.length === 0" description="暂无日志，等待活动..." />
      
      <div v-else class="log-list">
        <div
          v-for="(log, index) in logs"
          :key="index"
          class="log-item"
          :class="`log-${log.type}`"
        >
          <div class="log-time">
            <icon-clock-circle />
            {{ log.time }}
          </div>
          <div class="log-content">
            <a-tag v-if="log.type !== 'default'" :color="getTagColor(log.type)" size="small">
              {{ getTypeLabel(log.type) }}
            </a-tag>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="log-input-area">
      <a-input-search
        v-model="inputMessage"
        placeholder="输入测试消息..."
        :button-props="{ type: 'primary' }"
        @search="addCustomLog"
      >
        <template #button-icon>
          <icon-send />
        </template>
      </a-input-search>
    </div>
  </a-card>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { 
  IconFile,
  IconDelete, 
  IconDownload, 
  IconClockCircle,
  IconSend 
} from '@arco-design/web-vue/es/icon'

// 日志类型
const LogType = {
  DEFAULT: 'default',
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
}

// 响应式数据
const logs = ref([])
const inputMessage = ref('')
const logContainerRef = ref(null)

// 获取标签颜色
const getTagColor = (type) => {
  const colors = {
    [LogType.INFO]: 'arcoblue',
    [LogType.SUCCESS]: 'green',
    [LogType.WARNING]: 'orange',
    [LogType.ERROR]: 'red'
  }
  return colors[type] || 'gray'
}

// 获取类型标签
const getTypeLabel = (type) => {
  const labels = {
    [LogType.INFO]: '信息',
    [LogType.SUCCESS]: '成功',
    [LogType.WARNING]: '警告',
    [LogType.ERROR]: '错误'
  }
  return labels[type] || type
}

// 添加日志
const addLog = async (message, type = LogType.DEFAULT) => {
  const log = {
    time: new Date().toLocaleTimeString(),
    message,
    type
  }
  logs.value.push(log)
  
  // 限制日志数量，保留最新的 100 条
  if (logs.value.length > 100) {
    logs.value = logs.value.slice(-100)
  }
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
}

// 添加自定义日志（从输入框）
const addCustomLog = () => {
  if (!inputMessage.value.trim()) return
  addLog(inputMessage.value, LogType.INFO)
  inputMessage.value = ''
}

// 清空日志
const clearLogs = () => {
  logs.value = []
  addLog('日志已清空', LogType.INFO)
}

// 导出日志
const exportLogs = () => {
  const content = logs.value.map(log => `[${log.time}] [${log.type.toUpperCase()}] ${log.message}`).join('\n')
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `logs_${new Date().toISOString().slice(0, 10)}.txt`
  link.click()
  URL.revokeObjectURL(url)
  addLog('日志已导出', LogType.SUCCESS)
}

// 滚动到底部
const scrollToBottom = () => {
  if (logContainerRef.value) {
    logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
  }
}

// 暴露方法给父组件
defineExpose({
  addLog,
  clearLogs,
  logs
})
</script>

<style scoped>
.log-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.log-container {
  height: 300px;
  overflow-y: auto;
  background: #f7f8fa;
  border-radius: 4px;
  padding: 12px;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border-left: 3px solid #e5e6eb;
  transition: all 0.2s;
}

.log-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.log-info {
  border-left-color: #165dff;
}

.log-success {
  border-left-color: #00b42a;
}

.log-warning {
  border-left-color: #ff7d00;
}

.log-error {
  border-left-color: #f53f3f;
}

.log-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #86909c;
}

.log-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.log-message {
  color: #1d2129;
  font-size: 14px;
}

.log-input-area {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e6eb;
}

:deep(.arco-card-body) {
  padding: 16px;
}

:deep(.arco-card-header) {
  padding: 16px;
  border-bottom: 1px solid #e5e6eb;
}
</style>
