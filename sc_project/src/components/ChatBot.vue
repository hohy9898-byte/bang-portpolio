<script setup>
import { ref, nextTick, onMounted } from "vue";
import { askGPT } from "../services/openai";

const props = defineProps({
  initialQuestion: {
    type: String,
    default: ""
  }
});

const input = ref("");
const menu = ref("main");
const history = ref(null);
const isLoading = ref(false);

const messages = ref([
  {
    role: "assistant",
    text: `안녕하세요 😊

축제, 어디까지 가는 거예요? 부산 관광 챗봇입니다.

원하는 메뉴를 선택해주세요.`
  }
]);

async function sendMessage(category = null) {
  if (!input.value.trim() || isLoading.value) return;

  const question = input.value;

  messages.value.push({
    role: "user",
    text: question
  });

  input.value = "";
  isLoading.value = true;

  await scrollBottom();

  try {
    const answer = await askGPT(question);

    messages.value.push({
      role: "assistant",
      text: answer,
      category
    });
  } catch (e) {
    messages.value.push({
      role: "assistant",
      text: `⚠️ 오류가 발생했습니다: ${e.message || "알 수 없는 오류"}`
    });
  }

  isLoading.value = false;

  await scrollBottom();
}

async function quickQuestion(text, category = null) {
  input.value = text;
  await sendMessage(category);
}

// 이번 달/다음 달 실제 연월을 계산해 정확한 날짜로 질문 (조원 코드 병합)
function askThisMonthFestival() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;

  quickQuestion(`${year}년 ${month}월 부산 축제 알려줘`);
}

function askNextMonthFestival() {
  const now = new Date();
  let year = now.getFullYear();
  let month = now.getMonth() + 2;

  if (month > 12) {
    month = 1;
    year++;
  }

  quickQuestion(`${year}년 ${month}월 부산 축제 알려줘`);
}

async function scrollBottom() {
  await nextTick();

  if (history.value) {
    history.value.scrollTop = history.value.scrollHeight;
  }
}

onMounted(() => {
  if (props.initialQuestion.trim()) {
    input.value = props.initialQuestion;
    sendMessage();
  }
});
</script>

<template>

<div class="chat">

  <!-- 헤더 -->
  <div class="header">
    🤖 축제, 어디까지 가는 거예요? AI 챗봇
  </div>

  <!-- 채팅창 -->
  <div class="history" ref="history">

    <div
      v-for="(m,index) in messages"
      :key="index"
      class="message"
      :class="m.role"
    >
      <div class="bubble" :class="{ center: m.category === 'stay' }">
        {{ m.text }}
      </div>
    </div>

    <div v-if="isLoading" class="message assistant">
      <div class="bubble typing">
        <span></span><span></span><span></span>
      </div>
    </div>

  </div>

  <!-- 메인 메뉴 -->
  <div class="quick-menu" v-if="menu==='main'">

    <button @click="menu='festival'">
      🎉 부산 축제
    </button>

    <button @click="quickQuestion('부산 관광지 추천해줘')">
      🏝 관광지
    </button>

    <button @click="quickQuestion('부산 숙박 추천해줘', 'stay')">
      🏨 숙박
    </button>

    <button @click="quickQuestion('부산 문화시설 추천해줘')">
      🎭 문화시설
    </button>

    <button @click="quickQuestion('부산 레포츠 추천해줘')">
      ⚽ 레포츠
    </button>

    <button @click="quickQuestion('부산 쇼핑 추천해줘')">
      🛍 쇼핑
    </button>

  </div>

  <!-- 축제 메뉴 -->
  <div class="quick-menu" v-if="menu==='festival'">

    <button @click="askThisMonthFestival()">
      📅 이번 달
    </button>

    <button @click="askNextMonthFestival()">
      🗓 다음 달
    </button>

    <button @click="quickQuestion('부산 축제 전체 알려줘')">
      📋 전체 축제
    </button>

    <button @click="menu='main'">
      ⬅ 메인으로
    </button>

  </div>

  <!-- 입력창 -->
  <div class="input-area">

    <input
      v-model="input"
      @keyup.enter="sendMessage"
      placeholder="질문을 입력하세요..."
      :disabled="isLoading"
    />

    <button @click="sendMessage" :disabled="isLoading">
      {{ isLoading ? '...' : '전송' }}
    </button>

  </div>

</div>

</template>

<style scoped>

.chat{
width:700px;
height:800px;
margin:150px auto;
display:flex;
flex-direction:column;
background:white;
border-radius:20px;
overflow:hidden;
box-shadow:0 15px 45px rgba(0,0,0,.2);
}

.header{
background:#0A84FF;
color:white;
padding:20px;
font-size:22px;
font-weight:bold;
text-align:center;
}

.quick-menu{
display:flex;
flex-wrap:wrap;
gap:10px;
padding:15px;
background:#f7f7f7;
border-top:1px solid #ddd;
}

.quick-menu button{
flex:1 1 calc(50% - 10px);
padding:12px;
border:none;
border-radius:10px;
background:#0A84FF;
color:white;
cursor:pointer;
}

.history{
    flex:1;
    overflow-y:auto;
    background:#f5f7fb;
    
    display:flex;
    flex-direction:column;


    padding:50px 25px 25px;
}

.message{
display:flex;
margin-bottom:15px;
}

.user{
justify-content:flex-end;
}

.assistant{
justify-content:flex-start;
}

.bubble{
padding:14px;
border-radius:18px;
max-width:75%;
white-space:pre-wrap;
}

.user .bubble{
background:#0A84FF;
color:white;
}

.assistant .bubble{
background:white;
border:1px solid #ddd;
text-align:left;
}

.assistant .bubble.center{
text-align:center;
}

.bubble.typing{
display:flex;
align-items:center;
gap:5px;
padding:16px 18px;
}

.bubble.typing span{
width:8px;
height:8px;
border-radius:50%;
background:#bbb;
animation:typing-bounce 1.2s infinite ease-in-out;
}

.bubble.typing span:nth-child(2){
animation-delay:0.2s;
}

.bubble.typing span:nth-child(3){
animation-delay:0.4s;
}

@keyframes typing-bounce{
0%, 60%, 100%{
transform:translateY(0);
opacity:0.5;
}
30%{
transform:translateY(-6px);
opacity:1;
}
}

.input-area{
display:flex;
padding:15px;
gap:10px;
}

.input-area input{
flex:1;
padding:12px;
border-radius:20px;
border:1px solid #ccc;
}

.input-area button{
padding:12px 20px;
border:none;
background:#0A84FF;
color:white;
border-radius:20px;
cursor:pointer;
}

.input-area input:disabled,
.input-area button:disabled{
opacity:0.6;
cursor:not-allowed;
}

</style>