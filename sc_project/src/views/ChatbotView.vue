<template>
  <div class="page-layout">
    <header class="topbar">
      <button type="button" class="logo" @click="goToMain">축제, 어디까지 가는 거예요?</button>
    </header>
  </div>

  <ChatBot :initial-question="initialQuestion" />
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import ChatBot from '../components/ChatBot.vue'

const route = useRoute()
const router = useRouter()
const initialQuestion = route.query.q || ''

function goToMain() {
  router.push('/')
}
</script>

<style scoped>
.logo {
  background: none;
  border: none;
  padding: 0;
  font-family: inherit;
  font-size: 16px;
  font-weight: 700;
  color: #1a73e8;
  cursor: pointer;
  white-space: nowrap;
}

.logo:hover {
  color: #1557b0;
}
</style>
