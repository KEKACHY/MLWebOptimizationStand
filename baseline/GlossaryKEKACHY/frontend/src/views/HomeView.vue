<template>
  <div class="layout">
    <Header></Header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Header from "@/components/Header.vue";
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.content {
  padding: 24px;
}
</style>