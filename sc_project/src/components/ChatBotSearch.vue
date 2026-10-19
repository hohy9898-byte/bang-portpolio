<template>
  <div class="search-container">
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input
        type="text"
        v-model="userInput"
        :placeholder="currentPlaceholder"
        class="search-input"
        @keyup.enter="askQuestion"
      />
      <button class="search-btn" @click="askQuestion">질문하기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const placeholders = [
  "광안리 놀러 갈 때 가 볼 축제 추천해 줘.",
  "부산 락 페스티벌 숙소 추천해줘.",
  "올해 여름 축제 일정 알려줘."
]

const currentPlaceholder = ref(placeholders[0])
const userInput = ref('')
let currentIndex = 0
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    currentIndex = (currentIndex + 1) % placeholders.length
    currentPlaceholder.value = placeholders[currentIndex]
  }, 3000)
})

onUnmounted(() => {
  clearInterval(timer)
})

const askQuestion = () => {
  const question = userInput.value.trim() || currentPlaceholder.value
  router.push({ path: '/chatbot', query: { q: question } })
}
</script>

<style scoped>
.search-container {
  width: 100%;
}

.search-box {
  display: flex;
  align-items: center;
  /* 안쪽으로 쏙 들어간 느낌의 뉴모피즘 검색창 */
  background: #f0f3f6;
  border-radius: 20px;
  padding: 12px 18px;
  border: none;
  box-shadow: inset 3px 3px 6px #d1d9e6, inset -3px -3px 6px #ffffff;
  transition: all 0.2s ease;
  width: 100%;
  max-width: none;
  box-sizing: border-box;
}

.search-icon {
  flex-shrink: 0;
  margin-right: 12px;
  font-size: 1.1rem;
  color: #a0aec0;
}

.search-input {
  flex: 1 1 auto;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.95rem;
  color: #4a5568;
  cursor: text;
  font-weight: 500;
}

.search-input::placeholder {
  color: #718096;
}

.search-btn {
  flex-shrink: 0;
  background: #1a73e8;
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 700;
  white-space: nowrap;
  box-shadow: 2px 2px 5px rgba(26, 115, 232, 0.25);
  transition: background 0.2s;
}

.search-btn:hover {
  background: #1557b0;
}
</style>