<template>
  <div class="festival-calendar" ref="rootEl">
    <button type="button" class="calendar-toggle" @click="toggleCalendar">📅</button>

    <div v-if="isOpen" class="calendar-panel">
      <div class="calendar-header">
        <button type="button" class="nav-btn" @click="prevMonth">‹</button>
        <span class="calendar-title">{{ viewYear }}년 {{ viewMonth + 1 }}월</span>
        <button type="button" class="nav-btn" @click="nextMonth">›</button>
      </div>

      <div class="weekday-row">
        <span v-for="w in ['일', '월', '화', '수', '목', '금', '토']" :key="w">{{ w }}</span>
      </div>

      <div class="day-grid">
        <span
          v-for="(cell, idx) in calendarDays"
          :key="idx"
          class="day-cell"
          :class="{
            empty: !cell,
            'has-festival': cell && cell.festivals.length > 0,
            selected: cell && selectedDay && selectedDay.day === cell.day
          }"
          @click="cell && selectDay(cell)"
        >
          {{ cell ? cell.day : '' }}
        </span>
      </div>

      <div v-if="selectedDay" class="selected-day-panel">
        <div class="selected-day-title" @click="askAboutDate(selectedDay)">
          🔍 {{ formatDateLabel(selectedDay.date) }}
        </div>

        <ul v-if="selectedDay.festivals.length" class="selected-festival-list">
          <li
            v-for="festival in selectedDay.festivals"
            :key="festival.contentid"
            class="selected-festival-item"
            @click="askAboutFestival(festival, selectedDay)"
          >
            <span class="festival-item-title">{{ festival.title }}</span>
            <span class="festival-item-period">{{ formatFestivalPeriod(festival) }}</span>
          </li>
        </ul>
        <p v-else class="no-festival-text">이 날짜엔 등록된 축제가 없습니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const rootEl = ref(null)
const isOpen = ref(false)
const festivals = ref([])

const today = new Date()
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth())
const selectedDay = ref(null)

function parseDateString(str) {
  if (!str) return null
  const y = parseInt(str.slice(0, 4))
  const m = parseInt(str.slice(4, 6)) - 1
  const d = parseInt(str.slice(6, 8))
  return new Date(y, m, d)
}

// 캘린더에는 축제 시작일만 표시 (기간 전체가 아니라 시작일 하루만 마킹)
function festivalsStartingOnDate(date) {
  return festivals.value.filter((f) => {
    const start = parseDateString(f.eventstartdate)
    if (!start) return false
    return (
      start.getFullYear() === date.getFullYear() &&
      start.getMonth() === date.getMonth() &&
      start.getDate() === date.getDate()
    )
  })
}

function pad2(n) {
  return String(n).padStart(2, '0')
}

function formatShortDate(date) {
  return `${date.getFullYear()}.${pad2(date.getMonth() + 1)}.${pad2(date.getDate())}`
}

// 선택된 날짜 정보에 표시할 축제 기간 (시작일~종료일)
function formatFestivalPeriod(festival) {
  const start = parseDateString(festival.eventstartdate)
  const end = parseDateString(festival.eventenddate)
  if (!start || !end) return ''
  if (start.getTime() === end.getTime()) return formatShortDate(start)
  return `${formatShortDate(start)} ~ ${formatShortDate(end)}`
}

const calendarDays = computed(() => {
  const firstDay = new Date(viewYear.value, viewMonth.value, 1)
  const startWeekday = firstDay.getDay()
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()

  const days = []
  for (let i = 0; i < startWeekday; i++) days.push(null)
  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(viewYear.value, viewMonth.value, d)
    days.push({ day: d, date, festivals: festivalsStartingOnDate(date) })
  }
  return days
})

function toggleCalendar() {
  isOpen.value = !isOpen.value
}

function prevMonth() {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value--
  } else {
    viewMonth.value--
  }
  selectedDay.value = null
}

function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value++
  } else {
    viewMonth.value++
  }
  selectedDay.value = null
}

function selectDay(cell) {
  selectedDay.value = cell
}

function formatDateLabel(date) {
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

function askAboutDate(day) {
  router.push({ path: '/chatbot', query: { q: `${formatDateLabel(day.date)} 부산 축제 알려줘` } })
}

function askAboutFestival(festival, day) {
  router.push({
    path: '/chatbot',
    query: { q: `${formatDateLabel(day.date)} ${festival.title} 축제 정보 알려줘` }
  })
}

function handleOutsideClick(event) {
  if (isOpen.value && rootEl.value && !rootEl.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleOutsideClick)

  try {
    const res = await fetch('/data/부산_축제공연행사.json')
    const json = await res.json()
    festivals.value = (json.items || []).filter((f) => f.eventstartdate && f.eventenddate)
  } catch (e) {
    festivals.value = []
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.festival-calendar {
  position: relative;
}

.calendar-toggle {
  border: 1px solid #d1d5db;
  border-radius: 999px;
  width: 52px;
  height: 52px;
  background: white;
  cursor: pointer;
  font-size: 1.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calendar-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  box-sizing: border-box;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  padding: 16px;
  z-index: 20;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.calendar-title {
  font-weight: 700;
  color: #1e293b;
}

.nav-btn {
  border: none;
  background: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #64748b;
  padding: 2px 8px;
}

.nav-btn:hover {
  color: #1a73e8;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 4px;
}

.day-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-auto-rows: 34px;
  gap: 2px;
}

.day-cell {
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
  color: #334155;
  border-radius: 8px;
  cursor: pointer;
}

.day-cell.empty {
  cursor: default;
}

.day-cell:not(.empty):not(.selected):hover {
  background: #f1f5f9;
}

.day-cell.has-festival {
  font-weight: 800;
  color: white;
  background: #1a73e8;
}

.day-cell.selected {
  background: #0d3d8c;
  color: white;
  box-shadow: 0 0 0 2px #0d3d8c;
}

.selected-day-panel {
  margin-top: 12px;
  border-top: 1px solid #e5e7eb;
  padding-top: 10px;
}

.selected-day-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e293b;
  cursor: pointer;
  margin-bottom: 6px;
}

.selected-day-title:hover {
  color: #1a73e8;
}

.selected-festival-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.selected-festival-item {
  display: flex;
  flex-direction: column;
  gap: 1px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
}

.festival-item-title {
  font-size: 0.82rem;
  color: #334155;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.festival-item-period {
  font-size: 0.72rem;
  color: #94a3b8;
}

.selected-festival-item:hover .festival-item-title {
  color: #1a73e8;
}

.selected-festival-item:hover {
  background: #eaf2fe;
}

.no-festival-text {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}
</style>
