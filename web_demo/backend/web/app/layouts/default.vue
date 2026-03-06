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

<style scoped>
.app {
  min-height: 100vh;
  padding: 24px;
  //background: #0f172a;
}

.page {
  max-width: 1400px;
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
