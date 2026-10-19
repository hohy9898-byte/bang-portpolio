<template>
  <div id="app-shell">
    <nav class="app-nav">
      <RouterLink to="/">홈</RouterLink>
      <RouterLink to="/board">게시판</RouterLink>
      <RouterLink to="/chatbot">AI 챗봇</RouterLink>
    </nav>

    <RouterView />
  </div>
</template>

<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<style scoped>
.app-nav {
  display: flex;
  gap: 16px;
  padding: 12px 24px;
  border-bottom: 1px solid #e5e5e5;
}

.app-nav a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
}

.app-nav a.router-link-active {
  color: #2c7a4b;
}
</style>
