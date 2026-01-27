<template>
  <DefaultLayout>
    <section class="glossary">
      <div class="cards-container">
        <Card
          v-for="card in cards"
          :key="card.keyword"
          :title="card.keyword"
          :description="card.description"
        />
      </div>
    </section>
  </DefaultLayout>
</template>

<script setup>
import { onMounted, ref } from "vue";
import Card from "./Card.vue";

const cards = ref([]);

onMounted(async () => {
  cards.value = await fetch("http://localhost:8000/glossaries/")
    .then(r => r.json());
});
</script>

<style lang="scss" scoped>
@use '@/assets/styles/glossary.scss' as *;
</style>