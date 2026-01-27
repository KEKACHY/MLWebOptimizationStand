<template>
  <header class="site-header">
    <nav>
      <router-link to="/" custom v-slot="{ navigate, isActive }">
        <button
          class="home-button"
          :class="{ active: isActive }"
          @click="navigate"
        >
          <img class="button-icon" src="@/assets/img/book.svg" alt="icon">
          <span class="button-text">Глоссарий</span>
        </button>
      </router-link>

      <router-link to="/graph" custom v-slot="{ navigate, isActive }">
        <button
          class="home-button"
          :class="{ active: isActive }"
          @click="navigate"
        >
          <img class="button-icon" src="@/assets/img/graph.svg" alt="icon">
          <span class="button-text">Семантический граф</span>
        </button>
      </router-link>
    </nav>
  </header>
</template>

<style lang="scss" scoped>
@use '@/assets/styles/header.scss' as *;
</style>