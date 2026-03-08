# Hunyuan3D Web Demo

这是 Hunyuan3D 项目的前端 Web 演示应用，基于 Nuxt.js 4 开发。

## 技术栈

- **框架**: Nuxt.js 4
- **语言**: TypeScript
- **UI 组件库**: Arco Design Vue
- **样式**: Tailwind CSS
- **3D 模型查看**: Three.js + GLTFLoader
- **状态管理**: Vue 3 Composition API
- **HTTP 客户端**: Fetch API

## 安装

### 前置要求

- Node.js 18.0 或更高版本
- npm 或 yarn

### 安装依赖

```bash
# 使用 npm
npm install

# 或使用 yarn
yarn install
```

## 运行

### 开发模式

```bash
# 使用 npm
npm run dev

# 或使用 yarn
yarn dev
```

开发服务器将在 `http://localhost:3000` 启动。

### 预览模式

```bash
# 使用 npm
npm run preview

# 或使用 yarn
yarn preview
```

## 构建

### 静态站点生成

```bash
# 使用 npm
npm run generate

# 或使用 yarn
yarn generate
```

静态文件将生成到 `static` 目录中。

### 生产构建

```bash
# 使用 npm
npm run build

# 或使用 yarn
yarn build
```

## 项目结构

```
├── components/           # Vue 组件目录
│   ├── HistorySidebar.vue    # 历史记录侧边栏组件
│   ├── LogPanel.vue          # 日志面板组件
│   └── ThreeViewer.vue       # 3D 模型查看器组件
├── pages/                # 页面目录
│   └── index.vue              # 主页面
├── composables/          # 组合式函数目录
│   ├── useHistory.js          # 历史记录管理
│   └── useModelGeneration.js   # 模型生成逻辑
├── layouts/              # 布局目录
│   └── default.vue            # 默认布局
├── public/               # 静态资源目录
├── ../static/            # 静态构建输出目录
├── nuxt.config.ts        # Nuxt 配置文件
├── package.json          # 项目依赖配置
└── README.md             # 项目说明文档
```

## 配置说明

### 代理配置

项目配置了 API 代理，将 `/api` 路径代理到 `http://localhost:8000`，可在 `nuxt.config.ts` 中修改：

```typescript
vite: {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
}
```

### 静态输出配置

静态站点生成的输出目录配置为 `static-output`，可在 `nuxt.config.ts` 中修改：

```typescript
nitro: {
  preset: 'static',
  output: {
    publicDir: './static-output'
  }
}
```

## 主要功能

### 1. 3D 模型生成
- 支持上传图片生成 3D 模型
- 提供速度优先和质量优先两种预设
- 实时显示生成进度和日志
- 支持自定义参数（steps、guidance、octree_resolution）

### 2. 3D 模型查看器
- 基于 Three.js 的实时 3D 预览
- 支持鼠标交互（旋转、缩放、平移）
- 自动调整模型大小和位置
- 支持多种数据源（ArrayBuffer、Blob URL、HTTP URL）

### 3. 历史记录管理
- 自动保存生成的模型到历史记录
- 可展开/收起的侧边栏设计
- 支持查看、下载、删除历史记录
- 显示文件名和时间戳

### 4. 本地 GLB 文件预览
- 支持上传本地 GLB 文件进行预览
- 无需生成即可查看 3D 模型

### 5. 日志面板
- 实时显示生成日志
- 自动滚动到最新日志
- 格式化的时间戳显示

## API 接口

### 历史记录相关
- `GET /api/history` - 获取历史记录列表
- `POST /api/history` - 添加历史记录
- `DELETE /api/history/{history_id}` - 删除历史记录

### 模型相关
- `GET /api/models/{filename}` - 获取模型文件

### 生成相关
- `POST /api/generate/image` - 上传图片并生成 3D 模型
- `GET /api/jobs/{job_id}` - 获取任务状态
- `GET /api/jobs/{job_id}/result` - 获取任务结果

## 注意事项

- 确保后端服务在 `http://localhost:8000` 运行，或修改代理配置以匹配实际后端地址
- 静态构建后，生成的文件可部署到任何静态文件服务器
- 开发过程中，可使用 Nuxt DevTools 进行调试（已启用）
- 历史记录数据存储在后端 SQLite 数据库中，重启后端服务不会丢失
- 3D 模型查看器需要浏览器支持 WebGL
- 本地上传的 GLB 文件仅在当前会话中有效，不会保存到历史记录
- 历史记录默认显示最近 10 条记录

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 开发指南

### 添加新组件

在 `components/` 目录下创建 Vue 组件，Nuxt 会自动导入：

```vue
<template>
  <div>
    <!-- 组件内容 -->
  </div>
</template>

<script setup>
// 组件逻辑
</script>
```

### 使用 Composable

在 `composables/` 目录下创建组合式函数，可以在任何组件中使用：

```javascript
export const useMyFeature = () => {
  const state = ref(null)
  
  const doSomething = () => {
    // 逻辑代码
  }
  
  return {
    state,
    doSomething
  }
}
```

### 样式开发

项目使用 Tailwind CSS，可以直接在组件中使用 Tailwind 类名：

```vue
<template>
  <div class="bg-blue-500 text-white p-4 rounded">
    Hello World
  </div>
</template>
```

## 故障排除

### 3D 模型无法显示
- 检查浏览器是否支持 WebGL
- 确认模型文件格式是否正确（GLB/GLTF）
- 查看浏览器控制台是否有错误信息

### 历史记录不显示
- 确认后端服务正常运行
- 检查 `/api/history` 接口是否正常返回数据
- 查看浏览器网络请求是否有错误

### 模型生成失败
- 检查上传的图片格式和大小
- 查看日志面板的错误信息
- 确认后端模型是否正常加载

## 许可证

MIT
