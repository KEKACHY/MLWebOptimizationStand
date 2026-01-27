<template>
  <div>
    <main>
      <slot></slot>
    </main>
  </div>
</template>

<script>
import Header from '@/components/Header.vue';

export default {
  name: 'DefaultLayout',
  components: { Header }
};
</script>

<style scoped>
main {
  padding: 20px;
}
</style>