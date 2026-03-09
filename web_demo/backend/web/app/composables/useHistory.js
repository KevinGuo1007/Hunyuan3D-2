import { ref } from 'vue'

export const useHistory = () => {
  const history = ref([])

  // 初始化历史记录
  const initHistory = async () => {
    if (process.client) {
      try {
        console.log('Loading history from API...')
        const response = await fetch('/api/history')
        if (response.ok) {
          const data = await response.json()
          history.value = data
          console.log('Loaded history items:', history.value.length)
        } else {
          console.error('Failed to load history:', response.status)
          history.value = []
        }
      } catch (error) {
        console.error('Failed to load history:', error)
        history.value = []
      }
    }
  }

  // 添加历史记录
  const addToHistory = async (filename, modelUrl) => {
    if (process.client) {
      try {
        // 检查是否是模型文件路径
        if (typeof modelUrl === 'string') {
          // 从 URL 中提取文件名
          let modelFilename, modelPath
          
          if (modelUrl.startsWith('/api/models/')) {
            // 处理直接的模型 URL
            modelFilename = modelUrl.split('/').pop()
            modelPath = `web_demo/outputs/${modelFilename}`
          } else if (modelUrl.startsWith('/api/jobs/')) {
            // 处理任务结果 URL
            // 从任务 ID 生成文件名
            const jobId = modelUrl.split('/')[3]
            modelFilename = `${jobId}.glb`
            modelPath = `web_demo/outputs/${modelFilename}`
          } else if (modelUrl.startsWith('blob:')) {
            // 对于本地上传的文件，跳过添加到历史记录
            // 因为这些文件只存在于浏览器中，没有保存到服务器
            console.warn('Local blob files not added to history')
            return
          } else {
            // 其他类型的 URL，跳过
            console.warn('Unknown model URL format:', modelUrl)
            return
          }
          
          // 调用后端 API 添加历史记录
          const response = await fetch('/api/history', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
              filename: filename,
              model_path: modelPath
            })
          })
          
          if (response.ok) {
            const newHistoryItem = await response.json()
            // 添加到历史记录开头
            history.value.unshift(newHistoryItem)
            // 限制历史记录数量
            if (history.value.length > 10) {
              history.value = history.value.slice(0, 10)
            }
            console.log('History added successfully')
          } else {
            console.error('Failed to add history:', response.status)
          }
        } else if (modelUrl instanceof ArrayBuffer) {
          // 对于上传的本地文件，暂时不添加到历史记录
          // 因为需要先保存到服务器
          console.warn('Local files not added to history yet')
        }
      } catch (error) {
        console.error('Failed to add history:', error)
      }
    }
  }

  // 删除历史记录项
  const deleteHistoryItem = async (id) => {
    if (process.client) {
      try {
        const response = await fetch(`/api/history/${id}`, {
          method: 'DELETE'
        })
        if (response.ok) {
          // 从本地列表中移除
          history.value = history.value.filter(item => item.id !== id)
          return true
        } else {
          console.error('Failed to delete history:', response.status)
          return false
        }
      } catch (error) {
        console.error('Failed to delete history:', error)
        return false
      }
    }
    return false
  }

  return {
    history,
    initHistory,
    addToHistory,
    deleteHistoryItem
  }
}