<template>
  <div class="card">
    <div class="card-inner">
      <div class="card-front">{{ title }}</div>
      <div class="card-back" :style="{ fontSize: fontSize + 'px' }" ref="back">
        {{ description }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: String,
    description: String
  },
  data() {
    return {
      fontSize: 16
    };
  },
  mounted() {
    this.adjustFont();
  },
  methods: {
    adjustFont() {
      const el = this.$refs.back;
      let font = 16;
      while(el.scrollHeight > el.clientHeight && font > 10) {
        font -= 1;
        this.fontSize = font;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
@use '@/assets/styles/card.scss' as *;
</style>