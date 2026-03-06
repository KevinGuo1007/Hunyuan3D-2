# Hunyuan3D Web Demo

这是 Hunyuan3D 项目的前端 Web 演示应用，基于 Nuxt.js 4 开发。

## 技术栈

- **框架**: Nuxt.js 4
- **语言**: TypeScript
- **UI 组件库**: Arco Design Vue
- **样式**: Tailwind CSS
- **3D 模型查看**: Google Model Viewer

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
├── components/       # 组件目录
├── pages/            # 页面目录
├── public/           # 静态资源目录
├── ../static/    # 静态构建输出目录
├── nuxt.config.ts    # Nuxt 配置文件
├── package.json      # 项目依赖配置
└── README.md         # 项目说明文档
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

## 注意事项

- 确保后端服务在 `http://localhost:8000` 运行，或修改代理配置以匹配实际后端地址
- 静态构建后，生成的文件可部署到任何静态文件服务器
- 开发过程中，可使用 Nuxt DevTools 进行调试（已启用）

## 许可证

MIT
