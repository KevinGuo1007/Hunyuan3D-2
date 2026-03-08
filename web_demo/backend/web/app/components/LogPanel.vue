<template>
  <section class="rounded-lg p-6 shadow-lg col-span-1 md:col-span-2">
    <div class="mb-2">
      <h2 class="text-xl font-bold text-white">Inference Logs</h2>
      <p class="text-sm text-gray-500">Realtime info from the current session</p>
    </div>
    <div class="h-[300px] overflow-y-auto rounded p-3 mt-3 border-2 rounded-2xl border-indigo-950 " id="log-box">
      <pre class="m-0 font-mono text-sm leading-relaxed text-white  whitespace-pre-wrap break-words">{{
          logOutput
        }}</pre>
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  logOutput: {
    type: String,
    default: 'Waiting for activity…'
  }
})
</script>