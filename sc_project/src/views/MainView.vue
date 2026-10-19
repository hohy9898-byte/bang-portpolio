<template>
  <div class="home-container">
    <div class="main-content-wrapper">

      <!-- 상단 영역: 화면 기준 가로/세로 완벽한 정중앙 정렬 배치의 중심 -->
      <section class="hero-section">

        <!-- 왼쪽 콘텐츠 세로 배열 (우측으로 5% 이동 레이아웃 반영) -->
        <div class="left-content">
          <!-- 메인 타이틀 -->
          <h1 class="main-title">축제, 어디까지 가는 거예요?</h1>

          <!-- 기존보다 1.5배 굵어진 회색 윤곽선 + 곡선형 말풍선 꼬리 -->
          <div class="speech-bubble-container">
            <div class="speech-bubble glass-panel text-gray-border">
              <ChatBotSearch />
              <!-- 캐릭터 쪽 모서리가 강조된 자연스러운 말풍선 꼬리 -->
              <div class="bubble-tail text-gray-border"></div>
            </div>
          </div>

          <!-- 기존보다 1.5배 굵어진 회색 윤곽선 적용 오늘의 인기글 영역 -->
          <div class="popular-posts-box glass-panel text-gray-border">
            <div class="posts-header">
              <span class="live-badge">LIVE</span>
              <span class="posts-title">오늘의 인기글 🔥</span>
            </div>
            <div class="posts-carousel-placeholder">
              <Transition name="fade" mode="out-in">
                <p
                  v-if="currentPopularPost"
                  :key="currentPopularPost.id"
                  class="placeholder-text popular-post-clickable"
                  @click="goToPopularPost(currentPopularPost.id)"
                >
                  💬 {{ currentPopularPost.title }}
                </p>
                <p v-else key="empty" class="placeholder-text empty">
                  오늘 작성된 인기글이 아직 없습니다.
                </p>
              </Transition>
            </div>
          </div>

          <!-- 현재 정렬 상태에서 왼쪽으로 5% 이동된 수다 떨기 버튼 -->
          <div class="button-container">
            <button class="community-tag-btn" @click="goToPage('/board')">
              👥 시민들과 수다 떨기
            </button>
          </div>
        </div>

        <!-- 오른쪽 캐릭터 이미지 영역 -->
        <div class="right-content">
          <div class="character-wrapper">
            <img src="/char-busan.webp" alt="부산 축제 마스코트 캐릭터" class="character-img" />
          </div>
        </div>
      </section>

      <!-- 하단 영역: 폰트 1.2배 확대 및 기존보다 10% 더 상단으로 밀어올린 축제 카드 섹션 -->
      <section class="festival-section">
        <h2 class="festival-section-title">✨ 지금 주목받는 부산 축제</h2>
        <div class="festival-grid">

          <!-- 축제 카드 반복 구간 (일정 정보 태그 제거 및 데이터 연동) -->
          <div
            v-for="(festival, index) in selectedFestivals"
            :key="festival.contentid || index"
            class="festival-card glass-panel text-gray-border"
          >
            <!-- 축제 이미지 (데이터에 firstimage가 있으면 표시, 없으면 플레이스홀더) -->
            <div class="card-image-placeholder">
              <img
                v-if="festival.firstimage"
                :src="festival.firstimage"
                :alt="festival.title"
                class="festival-img"
              />
              <span v-else>🌊 {{ festival.title }}</span>
            </div>

            <div class="card-info">
              <div class="card-title-row">
                <h3>{{ festival.title }}</h3>
                <span :class="['status-tag', getFestivalStatus(festival).className]">
                  {{ getFestivalStatus(festival).text }}
                </span>
              </div>
              <p class="desc">{{ getShortProgram(festival) }}</p>
              <p class="location-text">📍 {{ festival.eventplace || festival.addr1 || '부산광역시 일원' }}</p>
            </div>
          </div>

        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import ChatBotSearch from '../components/ChatBotSearch.vue'

const router = useRouter()
const selectedFestivals = ref([])

// 오늘의 인기글: 게시판(BoardView)과 동일한 선정 기준 및 저장소를 사용
const POSTS_STORAGE_KEY = 'community-posts'

let communityPosts = []
try {
  const raw = JSON.parse(localStorage.getItem(POSTS_STORAGE_KEY) || 'null')
  communityPosts = Array.isArray(raw) ? raw : []
} catch (e) {
  console.error('게시글 저장소 파싱 실패:', e)
  communityPosts = []
}

function isPopularPost(post) {
  const likes = Number(post.likes ?? 0)
  return post.category === 'popular' || likes >= 10
}

const todayPopularPosts = computed(() => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  return communityPosts
    .filter((post) => {
      const createdAt = post.createdAt ? new Date(post.createdAt) : null
      if (!createdAt || Number.isNaN(createdAt.getTime())) return false

      const createdDate = new Date(
        createdAt.getFullYear(),
        createdAt.getMonth(),
        createdAt.getDate()
      )

      return createdDate.getTime() === today.getTime() && isPopularPost(post)
    })
    .sort((a, b) => {
      const likeDiff = Number(b.likes ?? 0) - Number(a.likes ?? 0)
      if (likeDiff !== 0) return likeDiff
      return new Date(a.createdAt) - new Date(b.createdAt)
    })
    .slice(0, 8)
})

const todayPopularIndex = ref(0)
const currentPopularPost = computed(() => todayPopularPosts.value[todayPopularIndex.value] || null)

let popularRotationTimer = null

function advanceTodayPopular() {
  if (todayPopularPosts.value.length <= 1) return
  todayPopularIndex.value = (todayPopularIndex.value + 1) % todayPopularPosts.value.length
}

function goToPopularPost(id) {
  router.push({ path: '/board', hash: `#/post/${id}` })
}

// 실제 활용하실 JSON 데이터 형태 매핑
const festivalData = {
  "region": "부산",
  "contentType": "축제공연행사",
  "contentTypeId": 15,
  "total": 72,
  "items": [
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/92/4077792_image2_1.jpg", "title": "2026 부산국제불교박람회", "contentid": "2644679", "eventstartdate": "20260806", "eventenddate": "20260809", "eventplace": "BEXCO 부산 벡스코 제1전시장(3홀)", "program": "- 주요 프로그램 : 주제전 / 명상문화전 및 명상 공예전 / 명상 예술전 / 선명상 체험전 / 발우공양 및 사찰음식전 / 무대 프로그램 / 체험 프로그램 등\n\n1. 주제전" },
    { "addr1": "부산광역시 수영구 광안해변로 219 (광안동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/41/4065341_image2_1.jpg", "title": "2026 나이트레이스 인 부산", "contentid": "3498395", "eventstartdate": "20260801", "eventenddate": "20260801", "eventplace": "광안리 해수욕장 / 벡스코", "program": "1. 주요 프로그램 : 나이트레이스 (광안대교를 배경으로 하는 야간 러닝 이벤트)\n- 티켓 구매자에 한하여 참여 가능" },
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/57/4077757_image2_1.jpg", "title": "제48차 유네스코 세계유산위원회 특별공연 산화비 : HEXAGRAM 22", "contentid": "4077756", "eventstartdate": "20260723", "eventenddate": "20260724", "eventplace": "벡스코 오디토리움", "program": "- 주요 프로그램 : 공연\n- 부대 행사 및 프로그램" },
    { "addr1": "부산광역시 사상구 삼락동", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/06/4040606_image2_1.jpg", "title": "부산국제록페스티벌", "contentid": "140799", "eventstartdate": "20261002", "eventenddate": "20261004", "eventplace": "삼락생태공원", "program": "1. 메인프로그램 : 부산국제록페스티벌\n2. 부대프로그램" },
    { "addr1": "부산광역시 동구 이순신대로 164 (초량동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/70/4058670_image2_1.jpg", "title": "부산항축제", "contentid": "1007868", "eventstartdate": "20260619", "eventenddate": "20260620", "eventplace": "북항 친수공원 일원", "program": "개막행사, 부산항불꽃쇼, 부산항투어, 보트투어, 기타 체험·참여 프로그램 등" },
    { "addr1": "부산광역시 수영구 광안해변로 219 (광안동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/10/4066810_image2_1.JPG", "title": "광안리어방축제", "contentid": "506545", "eventstartdate": "20260612", "eventenddate": "20260614", "eventplace": "광안리해변 및 수영사적공원 일원", "program": "1. 메인프로그램 : 뮤지컬어방, 경상좌수사행렬 퍼레이드, 어방민속마을\n2. 부대프로그램" },
    { "addr1": "부산광역시 해운대구 수영강변대로 85 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/37/4069137_image2_1.jpg", "title": "2026 부산나이트워크42K", "contentid": "2991394", "eventstartdate": "20260829", "eventenddate": "20260830", "eventplace": "APEC나루공원", "program": "- 주요 프로그램 : 수영강 및 온천천 코스 걷기 (8K·16K·24K·42K) / 워밍업 스트레칭 등\n- 부대 행사" },
    { "addr1": "부산광역시 수영구 민락동 110-19", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/73/4070173_image2_1.jpg", "title": "2026 부산바다도서관", "contentid": "3497353", "eventstartdate": "20260613", "eventenddate": "20260705", "eventplace": "민락수변공원 일원", "program": "- 주요 프로그램 : 커뮤니티존(북스팟)\n- 부대 행사 및 프로그램" },
    { "addr1": "부산광역시 중구 용두산길 37-55 (광복동2가)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/73/4067473_image2_1.jpg", "title": "2026 용골 댄스 페스타", "contentid": "2952109", "eventstartdate": "20260620", "eventenddate": "20260620", "eventplace": "용두산공원 일원", "program": "- 주요 프로그램 : 청소년 댄스 경연대회\n- 부대 행사" },
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/26/4055726_image2_1.jpeg", "title": "세계유산위원회 대한민국관(K-Heritage House)", "contentid": "4055637", "eventstartdate": "20260720", "eventenddate": "20260729", "eventplace": "부산 벡스코 제1전시장 2B, 3", "program": "1. 유산의 과거·현재·미래\n-세계유산&유네스코관: 17개 세계유산" },
    { "addr1": "부산광역시 북구 덕천동 763", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/30/4054930_image2_1.jpg", "title": "부산 밀 페스티벌", "contentid": "3303393" },
    { "addr1": "부산광역시 중구 중앙동4가", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/81/4065381_image2_1.jpg", "title": "포트빌리지 부산 2026", "contentid": "3485135" },
    { "addr1": "부산광역시 해운대구 수영강변대로 120 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/90/4065290_image2_1.jpg", "title": "2026 부산푸드필름페스타", "contentid": "2719122" },
    { "addr1": "부산광역시 해운대구 수영강변대로 120 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/20/4064420_image2_1.jpg", "title": "부산국제매직페스티벌", "contentid": "1032770" },
    { "addr1": "부산광역시 영도구 해양로301번길 55", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/73/4060873_image2_1.jpg", "title": "글로벌 영도커피페스티벌", "contentid": "2841074" },
    { "addr1": "부산광역시 부산진구 시민공원로 73 (범전동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/63/4063563_image2_1.jpg", "title": "부산가족축제", "contentid": "2818494" },
    { "addr1": "부산광역시 해운대구 해운대해변로 280 (중동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/55/4025555_image2_1.jpg", "title": "해운대 모래축제", "contentid": "566822" },
    { "addr1": "부산광역시 해운대구 수영강변대로 120 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/84/4057984_image2_1.png", "title": "국제해양영화제 (KIOFF)", "contentid": "2661307" },
    { "addr1": "부산광역시 부산진구 시민공원로 73 (범전동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/90/4056890_image2_1.png", "title": "제6회 부산 봄꽃 전시회", "contentid": "4056794" },
    { "addr1": "부산광역시 중구 광복중앙로 13 (신창동1가)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/00/4061800_image2_1.JPG", "title": "작당페스타", "contentid": "3115722" },
    { "addr1": "부산광역시 부산진구 동성로112번길 121-1", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/31/4054831_image2_1.jpg", "title": "부산연등회", "contentid": "1553601" },
    { "addr1": "부산광역시 기장군 기장읍 기장해안로 605", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/20/4059220_image2_1.jpg", "title": "기장멸치축제", "contentid": "292977" },
    { "addr1": "부산광역시 해운대구 APEC로 30 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/66/4059066_image2_1.jpg", "title": "K-핸드메이드페어 부산 2026", "contentid": "2523149", "eventstartdate": "20260724", "eventenddate": "20260726", "eventplace": "벡스코 제2전시장", "program": "- 주요 프로그램 : 휴꾸존 기획존" },
    { "addr1": "부산광역시 해운대구 APEC로 30 (우동)", "firstimage": "", "title": "K-일러스트레이션페어 부산 2026", "contentid": "2704473", "eventstartdate": "20260724", "eventenddate": "20260726", "eventplace": "벡스코 제2전시장 A, B홀", "program": "- 주요 프로그램 : 일러스트레이션 관련 개인 및 기업 브랜드 전시 부스\n- 부대 행사" },
    { "addr1": "부산 강서구 대저1동 1-17", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/77/4046477_image2_1.JPG", "title": "강서 낙동강30리 벚꽃축제", "contentid": "2536122" },
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/42/4038942_image2_1.jpg", "title": "2026 대한민국 과학축제 with 부산과학축전", "contentid": "2740921" },
    { "addr1": "부산광역시 영도구 해양로301번길 55 (동삼동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/41/4054241_image2_1.png", "title": "구룡마을 벚꽃축제", "contentid": "3359409" },
    { "addr1": "부산광역시 연제구 세병로 84 (거제동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/55/4046355_image2_1.jpg", "title": "연제고분판타지축제", "contentid": "4046353" },
    { "addr1": "부산광역시 사상구 사상로223번길 40 (괘법동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/14/4041614_image2_1.jpg", "title": "사상 가로공원 벚꽃야장(野/夜) 페스티벌", "contentid": "4041281" },
    { "addr1": "부산광역시 강서구 대저1동", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/62/4041162_image2_1.jpg", "title": "제22회 부산도시농업박람회", "contentid": "1907888" },
    { "addr1": "부산광역시 동구 충장대로 206 (초량동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/79/4039679_image2_1.jpg", "title": "제14회 부산국제항만컨퍼런스", "contentid": "4033328" },
    { "addr1": "부산광역시 동래구 문화로 80 (명륜동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/43/3366443_image2_1.jpg", "title": "동래읍성역사축제", "contentid": "229048" },
    { "addr1": "부산광역시 금정구 장전온천천로 48 (장전동)", "firstimage": "https://tong.visitkorea.or.kr/cms/resource/40/4008540_image2_1.jpg", "title": "라라라 페스티벌", "contentid": "2484237" },
    { "addr1": "부산광역시 수영구 광안해변로 219 (광안동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/12/3518612_image2_1.jpeg", "title": "광안리 M(Marvelous) 드론 라이트쇼", "contentid": "2786391" },
    { "addr1": "부산광역시 해운대구 해운대해변로 280 (중동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/12/3576412_image2_1.jpg", "title": "해운대 빛축제", "contentid": "2048902" },
    { "addr1": "부산광역시 수영구 광안해변로 219 (광안동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/64/3579164_image2_1.png", "title": "카운트다운 부산", "contentid": "2702333" },
    { "addr1": "부산광역시 해운대구 수영강변대로 120 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/78/3569778_image2_1.jpg", "title": "크리스마스 빌리지 부산 2025", "contentid": "3437916" },
    { "addr1": "부산광역시 수영구 광남로 96 (광안동, 광안 포디움프레스티지 1)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/58/3579258_image2_1.jpg", "title": "게임 체험 팝업 전시 'Game-Playground'", "contentid": "3422647" },
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/25/3536625_image2_1.jpg", "title": "부산국제아동도서전", "contentid": "3345610" },
    { "addr1": "부산광역시 중구 광복로 72-1 (광복동2가)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/05/3576405_image2_1.JPG", "title": "광복로 겨울빛 트리축제", "contentid": "3576410" },
    { "addr1": "부산광역시 동래구 중앙대로 1324 (온천동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/72/3574272_image2_1.jpg", "title": "온천천 빛 축제", "contentid": "3434800" },
    { "addr1": "부산광역시 영도구 해양로301번길 45 (동삼동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/90/3561790_image2_1.jpg", "title": "영도다리축제", "contentid": "1080734" },
    { "addr1": "부산광역시 남구 유엔평화로76번길 1 (대연동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/43/3537143_image2_1.jpg", "title": "부산국제공연예술마켓", "contentid": "3006246" },
    { "addr1": "부산광역시 중구 용두산길 37-30 (광복동2가)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/63/3559563_image2_1.jpg", "title": "부산중구반려동물축제", "contentid": "3559571" },
    { "addr1": "부산광역시 서구 송도해변로 100 (암남동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/36/3547136_image2_1.jpg", "title": "부산고등어축제", "contentid": "1399532" },
    { "addr1": "부산광역시 중구 광복로 72-1 (광복동2가)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/44/3556944_image2_1.png", "title": "부산 스트릿 페스타 인 광복", "contentid": "3556962" },
    { "addr1": "부산광역시 수영구 민락로6번길 29 (민락동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/52/3555352_image2_1.png", "title": "옥토버페스타 인 광안리", "contentid": "3555363" },
    { "addr1": "부산광역시 Basin구 시민공원로 73 (범전동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/71/3553771_image2_1.jpg", "title": "2025 영호남 전통시장 박람회", "contentid": "2868776" },
    { "addr1": "부산광역시 중구 용미길9번길 6-45 (남포동1가)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/08/3550808_image2_1.jpg", "title": "유라리 건맥축제", "contentid": "3001170" },
    { "addr1": "부산광역시 부산진구 시민공원로 73 (범전동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/47/3359047_image2_1.jpg", "title": "부산종합민속예술제", "contentid": "3016659" },
    { "addr1": "부산광역시 부산진구 전포동", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/54/3549654_image2_1.png", "title": "전포커피축제", "contentid": "3018117" },
    { "addr1": "부산광역시 금정구 남산로 27 (남산동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/48/3552448_image2_1.jpg", "title": "글로컬 문화 in(人) 남산 페스티벌", "contentid": "3020552" },
    { "addr1": "부산광역시 기장군 일광읍 칠암리", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/29/3553829_image2_1.JPG", "title": "기장붕장어축제in칠암", "contentid": "2860868" },
    { "addr1": "부산광역시 해운대구 수영강변대로 140 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/04/3531704_image2_1.png", "title": "부산글로벌웹툰페스티벌", "contentid": "2873292" },
    { "addr1": "부산광역시 사상구 삼락동", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/40/3539740_image2_1.png", "title": "사상강변축제", "contentid": "2032436" },
    { "addr1": "부산광역시 금정구 장전온천천로 48 (장전동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/24/3534524_image2_1.jpg", "title": "부산국제공연예술제", "contentid": "2558735" },
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/53/3536453_image2_1.jpg", "title": "부산수제맥주마스터스챌린지", "contentid": "2856938" },
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/68/3533968_image2_1.jpg", "title": "페스티벌 시월", "contentid": "3370514" },
    { "addr1": "부산광역시 서구 송도해변로 36 (암남동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/55/3532955_image2_1.jpg", "title": "부산 서구 의료관광축제", "contentid": "3532971" },
    { "addr1": "부산광역시 중구 충장대로 26 (중앙동4가)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/60/3532060_image2_1.JPG", "title": "중구민의 날 페스타", "contentid": "3351515" },
    { "addr1": "부산광역시 기장군 기장읍 동부산관광6로 59", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/93/3525493_image2_1.png", "title": "헬로메이커", "contentid": "2560161" },
    { "addr1": "부산광역시 금정구 장전로12번길 55 (장전동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/62/3528962_image2_1.png", "title": "2025 부산세일페스타 부대앞으로", "contentid": "3528964" },
    { "addr1": "부산광역시 사하구 몰운대1길 14 (다대동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/23/3524123_image2_1.jpg", "title": "2025 서부산 슈퍼어싱 페스티벌", "contentid": "3524130" },
    { "addr1": "부산광역시 북구 생태공원길 270 (화명동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/89/3524089_image2_1.png", "title": "2025 별바다부산 나이트마켓", "contentid": "3356047" },
    { "addr1": "부산광역시 영도구 해양로301번길 55 (동삼동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/09/3495409_image2_1.png", "title": "제2회 선원의날 한마음 걷기축제", "contentid": "3495410" },
    { "addr1": "부산광역시 기장군 장안읍 임랑리", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/82/3516182_image2_1.png", "title": "기장임랑썸머뮤직페스티벌", "contentid": "2614130" },
    { "addr1": "부산광역시 해운대구 수영강변대로 120 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/10/3515310_image2_1.jpg", "title": "부산국제AI영화제", "contentid": "3515311" },
    { "addr1": "부산광역시 사하구 다대동", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/21/2553821_image2_1.jpg", "title": "대한민국 국제해양레저위크(KIMA WEEK)", "contentid": "2019366" },
    { "addr1": "부산광역시 해운대구 APEC로 55 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/37/3510437_image2_1.jpg", "title": "부산인디커넥트페스티벌", "contentid": "2736033" },
    { "addr1": "부산광역시 사하구 다대포 해수욕장", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/58/3504958_image2_1.jpg", "title": "부산바다축제", "contentid": "142080", "eventstartdate": "20260807", "eventenddate": "20260813", "eventplace": "다대포 해수욕장 일원", "program": "1. 메인프로그램\n- 개막행사" },
    { "addr1": "부산광역시 해운대구 수영강변대로 120 (우동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/85/3502985_image2_1.png", "title": "2025 부산여행영화제", "contentid": "2830695" },
    { "addr1": "부산광역시 사하구 다대로 지하692 (다대동)", "firstimage": "http://tong.visitkorea.or.kr/cms/resource/05/3502005_image2_1.jpg", "title": "다대포 선셋 영화 축제", "contentid": "3383748" }
  ]
}

// YYYYMMDD 형태 문자열을 Date 객체로 파싱 변환 (조원 코드 병합)
const parseDateString = (dateStr) => {
  if (!dateStr) return null
  const year = parseInt(dateStr.substring(0, 4))
  const month = parseInt(dateStr.substring(4, 6)) - 1
  const day = parseInt(dateStr.substring(6, 8))
  return new Date(year, month, day)
}

// 진행중 / D-Day / 종료 상태 배지 도출 (조원 코드 병합)
function getFestivalStatus(festival) {
  const start = parseDateString(festival.eventstartdate)
  const end = parseDateString(festival.eventenddate)

  if (!start || !end) return { text: '미정', className: 'bg-slate-200 text-slate-600' }

  const today = new Date()
  const sDate = new Date(start.getFullYear(), start.getMonth(), start.getDate())
  const eDate = new Date(end.getFullYear(), end.getMonth(), end.getDate())
  const tDate = new Date(today.getFullYear(), today.getMonth(), today.getDate())

  if (tDate >= sDate && tDate <= eDate) {
    return { text: '진행중', className: 'bg-emerald-100 text-emerald-700 font-extrabold' }
  } else if (tDate < sDate) {
    const diffDays = Math.ceil((sDate.getTime() - tDate.getTime()) / (1000 * 60 * 60 * 24))
    return { text: `D-${diffDays}`, className: 'bg-blue-100 text-blue-700 font-extrabold' }
  } else {
    return { text: '종료', className: 'bg-rose-100 text-gray-400' }
  }
}

// 프로그램 설명 첫 줄만 추출 (조원 코드 병합)
function getShortProgram(festival) {
  if (!festival.program) return festival.addr1 || '상세 프로그램 정보 준비 중입니다.'
  return festival.program.split('\n')[0]
}

// 컴포넌트 마운트 시 진행중/한 달 이내 시작하는 축제 중 무작위 2개 추출 (조원 코드 병합)
onMounted(() => {
  const items = festivalData.items
  const today = new Date()
  const oneMonthLater = new Date(today)
  oneMonthLater.setMonth(today.getMonth() + 1)

  const eligibleFestivals = items.filter((item) => {
    const start = parseDateString(item.eventstartdate)
    const end = parseDateString(item.eventenddate)
    if (!start || !end) return false

    const isOngoing = today >= start && today <= end
    const isWithinOneMonth = start >= today && start <= oneMonthLater

    return isOngoing || isWithinOneMonth
  })

  const pool = eligibleFestivals.length >= 2 ? eligibleFestivals : items

  if (pool && pool.length >= 2) {
    // 원본 데이터를 해치지 않기 위해 얕은 복사 후 셔플 진행
    const shuffled = [...pool].sort(() => 0.5 - Math.random())
    selectedFestivals.value = shuffled.slice(0, 2)
  } else {
    selectedFestivals.value = pool || []
  }

  if (todayPopularPosts.value.length > 1) {
    popularRotationTimer = window.setInterval(advanceTodayPopular, 5000)
  }
})

onBeforeUnmount(() => {
  if (popularRotationTimer) {
    window.clearInterval(popularRotationTimer)
    popularRotationTimer = null
  }
})

const goToPage = (path) => {
  router.push(path)
}
</script>

<style scoped>
/* 전체 레이아웃 (스크롤 절대 방지 고정) */
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 50px);
  width: 100vw;
  box-sizing: border-box;
  padding: 10px 40px;
  font-family: 'Pretendard', sans-serif;
  position: relative;
  overflow: hidden;
}

.home-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.45;
  z-index: -1;
}

/* ✨ 공통 글래스모피즘 템플릿 */
.glass-panel {
  background: rgba(255, 255, 255, 0.55) !important;
  backdrop-filter: blur(14px) !important;
  -webkit-backdrop-filter: blur(14px) !important;
  box-shadow: 0 4px 24px 0 rgba(31, 38, 135, 0.02) !important;
}

/* 윤곽선 두께 기존 1.5px에서 정확히 1.5배 올린 2.25px 커스텀 고정 */
.text-gray-border {
  border: 2.25px solid #dee2e6 !important;
}

/* 메인 구조 콘텐트 래퍼 */
.main-content-wrapper {
  max-width: 1200px;
  width: 100%;
  height: 98%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

/* 상단 요소 전체 정중앙 배치 */
.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 50px;
  width: 100%;
  flex-grow: 1;
}

@media (max-width: 1024px) {
  .hero-section {
    flex-direction: column-reverse;
    text-align: center;
    gap: 25px;
  }
}

/* 좌측 텍스트/말풍선 영역 (우측으로 5% 배율 인덴트 고정) */
.left-content {
  flex: 1.5;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-left: 5%;
}

@media (max-width: 1024px) {
  .left-content {
    padding-left: 0;
  }
}

/* 타이틀 스타일 */
.main-title {
  font-size: 30pt;
  font-weight: 900;
  color: #1a73e8;
  margin-top: 0px;
  margin-bottom: 30px;
  letter-spacing: -0.5px;
  text-align: center;
  line-height: 1.2;
}

/* 말풍선 컨테이너 */
.speech-bubble-container {
  width: 100%;
  margin-bottom: 24px;
}

.speech-bubble {
  position: relative;
  border-radius: 24px;
  padding: 14px 10px;
  width: 100%;
  box-sizing: border-box;
}

/* 윤곽선 두께가 2.25px로 두꺼워진 말풍선 꼬리 디자인 */
.bubble-tail {
  position: absolute;
  top: 50%;
  right: -11.2px;
  transform: translateY(-50%) rotate(45deg);
  width: 19.2px;
  height: 19.2px;
  background: rgba(255, 255, 255, 0.55);
  border-top: 2.25px solid #dee2e6 !important;
  border-right: 2.25px solid #dee2e6 !important;
  border-bottom: transparent !important;
  border-left: transparent !important;
  border-radius: 3.5px;
  z-index: 2;
}

@media (max-width: 1024px) {
  .bubble-tail {
    top: -11.2px;
    right: 50%;
    transform: translateX(50%) rotate(-45deg);
    border-top: 2.25px solid #dee2e6 !important;
    border-left: 2.25px solid #dee2e6 !important;
    border-right: transparent !important;
    border-bottom: transparent !important;
  }
}

/* 오늘의 인기글 박스 */
.popular-posts-box {
  border-radius: 20px;
  padding: 16px 25px;
  margin-bottom: 24px;
  text-align: left;
}

.posts-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.live-badge {
  background: #ea4335;
  color: white;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 5px;
}

.posts-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #334155;
}

.posts-carousel-placeholder {
  min-height: 70px;
  display: flex;
  align-items: center;
}

.placeholder-text {
  margin: 0;
  font-size: 1rem;
  color: #475569;
  font-weight: 600;
}

.placeholder-text.popular-post-clickable {
  cursor: pointer;
}

.placeholder-text.popular-post-clickable:hover {
  color: #1a73e8;
}

.placeholder-text.empty {
  color: #94a3b8;
  font-weight: 500;
}

/* 부모 플렉스 상자 내부에서 왼쪽으로 5% 마진을 당겨 좌측 이동 보정 */
.button-container {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-left: -5%;
}

@media (max-width: 1024px) {
  .button-container {
    margin-left: 0;
  }
}

/* #dee2e6 색상 솔리드 버튼 스타일 */
.community-tag-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #dee2e6;
  border: 2.25px solid #dee2e6;
  padding: 8px 24px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 800;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}

.community-tag-btn:hover {
  color: #1a73e8;
  background: #cbd5e1;
  border-color: #cbd5e1;
}

/* 오른쪽 마스코트 캐릭터 영역 */
.right-content {
  flex: 0.8;
  display: flex;
  justify-content: center;
  align-items: center;
}

.character-img {
  width: 480px;
  height: auto;
  object-fit: contain;
}

/* 하단 축제 카드 영역: 기존 위치(-240px)보다 10% 추가 상단화 적용 (-265px) */
.festival-section {
  width: 100%;
  margin-top: -265px;
  padding-bottom: 5px;
}

/* 타이틀 폰트 크기 기존 1.25rem에서 1.2배 늘어난 1.5rem으로 고도화 */
.festival-section-title {
  font-size: 1.5rem;
  font-weight: 900;
  color: #1e293b;
  margin-bottom: 4px;
  text-align: left;
}

.festival-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.festival-card {
  border-radius: 24px;
  padding: 12px;
  transition: transform 0.2s;
}

.festival-card:hover {
  transform: translateY(-2px);
}

/* 카드 이미지 높이: 장소 텍스트 라인 추가분을 확보하기 위해 280px에서 축소 */
.card-image-placeholder {
  width: 100%;
  height: 235px;
  background: rgba(226, 232, 240, 0.7);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #64748b;
  font-size: 0.95rem;
  margin-bottom: 10px;
  overflow: hidden; /* 이미지가 카드 모서리를 깎아내지 않도록 방지 */
}

.festival-img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 이미지가 영역을 가득 채우도록 스타일링 */
}

.card-info {
  text-align: left;
  padding: 2px 4px;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 2px;
}

.card-title-row h3 {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

/* 진행중/D-Day/종료 상태 배지 (조원 코드 병합) */
.status-tag {
  font-size: 0.72rem;
  padding: 3px 10px;
  border-radius: 6px;
  white-space: nowrap;
  flex-shrink: 0;
}

.bg-slate-200 { background: #e2e8f0; }
.text-slate-600 { color: #475569; }
.bg-emerald-100 { background: #d1fae5; }
.text-emerald-700 { color: #047857; }
.bg-blue-100 { background: #dbeafe; }
.text-blue-700 { color: #1d4ed8; }
.bg-rose-100 { background: #ffe4e6; }
.text-gray-400 { color: #94a3b8; }
.font-extrabold { font-weight: 800; }

.card-info .desc {
  font-size: 0.82rem;
  color: #475569;
  margin: 0 0 2px 0;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* 프로그램 설명이 너무 길어질 경우 말줄임표 처리 */
}

/* 축제 장소 표시 (조원 코드 병합) */
.location-text {
  font-size: 0.78rem;
  color: #94a3b8;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
