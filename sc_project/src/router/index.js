import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import BoardView from '../views/BoardView.vue'
import ChatbotView from '../views/ChatbotView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'main', component: MainView },
    { path: '/board', name: 'board', component: BoardView },
    { path: '/chatbot', name: 'chatbot', component: ChatbotView }
  ]
})

export default router
