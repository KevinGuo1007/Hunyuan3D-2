<template>
  <div class="app">
    <main class="page">
      <slot />
    </main>
    <footer class="footer">
      <p>made by 无畏契约赋能组</p>
    </footer>
  </div>
</template>

<script>
export default {
  head() {
    return {
      script: [
        {
          src: 'https://unpkg.com/@google/model-viewer@latest/dist/model-viewer.js',
          defer: true,
          async: true
        }
      ]
    }
  }
}
</script>

<style>
/* 全局样式 - 隐藏滚动条但保留滚动功能 */
::-webkit-scrollbar {
  width: 0;
  height: 0;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: transparent;
}

/* 火狐浏览器 */
* {
  scrollbar-width: none;
  scrollbar-color: transparent transparent;
}
</style>

<style scoped>
.app {
  min-height: 100vh;
  padding: 24px;
  background: #0f172a;
  overflow: hidden;
}

.page {
  max-width: 100%;
  margin: 0 auto;
}

.footer {
  text-align: center;
  padding: 24px;
  color: #86909c;
  font-size: 14px;
  margin-top: 24px;
}
</style>
