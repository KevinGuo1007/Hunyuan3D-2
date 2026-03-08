<template>
  <div class="w-full h-full">
    <div ref="container" class="w-full h-full"></div>
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="text-white">Loading 3D model...</div>
    </div>
    <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="text-red-400">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const props = defineProps({
  modelUrl: {
    type: [String, ArrayBuffer],
    required: true
  }
})

const container = ref(null)
const loading = ref(true)
const error = ref('')

let scene = null
let camera = null
let renderer = null
let controls = null
let model = null
let animationId = null

const initThree = () => {
  // 创建场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x1a1a2e)

  // 创建相机
  camera = new THREE.PerspectiveCamera(75, container.value.clientWidth / container.value.clientHeight, 0.1, 1000)
  camera.position.z = 5

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(container.value.clientWidth, container.value.clientHeight)
  container.value.appendChild(renderer.domElement)

  // 添加轨道控制器
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05

  // 添加环境光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)

  // 添加平行光
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(1, 1, 1)
  scene.add(directionalLight)

  // 加载模型
  loadModel()

  // 开始动画循环
  animate()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

const loadModel = () => {
  const loader = new GLTFLoader()
  
  // 检查是否是 ArrayBuffer（直接从文件读取）
  if (props.modelUrl instanceof ArrayBuffer) {
    // 对于 ArrayBuffer，直接解析
    loader.parse(
      props.modelUrl,
      '',
      (gltf) => {
        model = gltf.scene
        scene.add(model)
        
        // 自动调整模型大小和位置
        const box = new THREE.Box3().setFromObject(model)
        const size = new THREE.Vector3()
        box.getSize(size)
        const maxSize = Math.max(size.x, size.y, size.z)
        const scale = 3 / maxSize
        model.scale.set(scale, scale, scale)
        
        // 居中模型
        const center = new THREE.Vector3()
        box.getCenter(center)
        model.position.sub(center)
        
        loading.value = false
        error.value = ''
      },
      (err) => {
        console.error('Error parsing model:', err)
        loading.value = false
        error.value = `Failed to parse 3D model: ${err.message || 'Unknown error'}`
      }
    )
  } else if (typeof props.modelUrl === 'string') {
    if (props.modelUrl.startsWith('blob:')) {
      // 对于 blob URL，使用 XMLHttpRequest 读取
      const xhr = new XMLHttpRequest()
      xhr.open('GET', props.modelUrl, true)
      xhr.responseType = 'arraybuffer'
      
      xhr.onload = function() {
        if (xhr.status === 200) {
          loader.parse(
            xhr.response,
            '',
            (gltf) => {
              model = gltf.scene
              scene.add(model)
              
              // 自动调整模型大小和位置
              const box = new THREE.Box3().setFromObject(model)
              const size = new THREE.Vector3()
              box.getSize(size)
              const maxSize = Math.max(size.x, size.y, size.z)
              const scale = 3 / maxSize
              model.scale.set(scale, scale, scale)
              
              // 居中模型
              const center = new THREE.Vector3()
              box.getCenter(center)
              model.position.sub(center)
              
              loading.value = false
              error.value = ''
            },
            (err) => {
              console.error('Error parsing model:', err)
              loading.value = false
              error.value = `Failed to parse 3D model: ${err.message || 'Unknown error'}`
            }
          )
        } else {
          loading.value = false
          error.value = `Failed to load model: HTTP ${xhr.status}`
        }
      }
      
      xhr.onerror = function() {
        loading.value = false
        error.value = 'Failed to load model: Network error'
      }
      
      xhr.send()
    } else if (props.modelUrl.startsWith('http://') || props.modelUrl.startsWith('https://') || props.modelUrl.startsWith('/api/')) {
      // 对于远程 URL，使用常规加载
      loader.load(
        props.modelUrl,
        (gltf) => {
          model = gltf.scene
          scene.add(model)
          
          // 自动调整模型大小和位置
          const box = new THREE.Box3().setFromObject(model)
          const size = new THREE.Vector3()
          box.getSize(size)
          const maxSize = Math.max(size.x, size.y, size.z)
          const scale = 3 / maxSize
          model.scale.set(scale, scale, scale)
          
          // 居中模型
          const center = new THREE.Vector3()
          box.getCenter(center)
          model.position.sub(center)
          
          loading.value = false
          error.value = ''
        },
        (xhr) => {
          console.log((xhr.loaded / xhr.total * 100) + '% loaded')
        },
        (err) => {
          console.error('Error loading model:', err)
          loading.value = false
          error.value = `Failed to load 3D model: ${err.message || 'Unknown error'}`
        }
      )
    } else {
      // 其他情况
      loading.value = false
      error.value = 'Invalid model URL'
    }
  } else {
    // 无效的 modelUrl 类型
    loading.value = false
    error.value = 'Invalid model URL type'
  }
}

const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  controls.update()
  renderer.render(scene, camera)
}

const handleResize = () => {
  if (!container.value || !camera || !renderer) return
  
  const width = container.value.clientWidth
  const height = container.value.clientHeight
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  
  renderer.setSize(width, height)
}

const cleanup = () => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  
  window.removeEventListener('resize', handleResize)
  
  if (renderer) {
    if (renderer.domElement && container.value) {
      container.value.removeChild(renderer.domElement)
    }
    renderer.dispose()
  }
  
  if (scene) {
    scene.traverse((object) => {
      if (object.geometry) object.geometry.dispose()
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose())
        } else {
          object.material.dispose()
        }
      }
    })
  }
}

watch(
  () => props.modelUrl,
  (newUrl) => {
    cleanup()
    loading.value = true
    error.value = ''
    initThree()
  }
)

onMounted(() => {
  if (container.value && props.modelUrl) {
    initThree()
  }
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.container {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>