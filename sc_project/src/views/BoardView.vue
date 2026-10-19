<template>
  <div id="app" class="page-layout">
    <header class="topbar">
      <button type="button" class="logo" @click="goToMain">축제, 어디까지 가는 거예요?</button>
      <nav class="category-nav">
        <button :class="{ active: selectedCategory === 'all' }" @click="selectCategory('all')">전체</button>
        <button :class="{ active: selectedCategory === 'festival' }" @click="selectCategory('festival')">축제</button>
        <button :class="{ active: selectedCategory === 'accommodation' }" @click="selectCategory('accommodation')">숙박</button>
        <button :class="{ active: selectedCategory === 'find' }" @click="selectCategory('find')">찾기</button>
        <button :class="{ active: selectedCategory === 'free' }" @click="selectCategory('free')">자유</button>
      </nav>
      <FestivalCalendar />
    </header>

    <section class="today-popular-section">
      <div class="today-popular-head">
        <h2>오늘의 인기글</h2>
      </div>

      <div class="today-popular-viewport">
        <Transition name="fade" mode="out-in">
          <div
            v-if="currentPopularPost"
            :key="currentPopularPost.id"
            class="today-popular-item today-popular-item-clickable"
            @click="openDetail(currentPopularPost.id)"
            @keydown.enter.prevent="openDetail(currentPopularPost.id)"
            tabindex="0"
            role="button"
          >
            <span class="today-popular-title">{{ currentPopularPost.title }}</span>
          </div>
          <div v-else :key="'empty'" class="today-popular-item">
            <span class="today-popular-title empty">오늘 작성된 인기글이 아직 없습니다.</span>
          </div>
        </Transition>
      </div>
    </section>

    <section class="board-header">
      <div class="breadcrumb">홈 &gt; {{ getCategoryLabel(selectedCategory) }} 게시판</div>

      <div class="board-actions">
        <div class="search-actions">
          <div class="search-toolbar">
            <div class="search-box">
              <input v-model="query" type="text" placeholder="게시글 검색어를 입력하세요" />
              <button @click="applySearch">검색</button>
            </div>
          </div>

          <div class="write-actions">
            <button class="new-post" @click="openCreateModal">+ 글쓰기</button>

            <div class="tab-group">
              <button :class="{ active: selectedTab === 'all' }" @click="selectedTab = 'all'">전체</button>
              <button :class="{ active: selectedTab === 'popular' }" @click="selectedTab = 'popular'">인기글</button>
              <button :class="{ active: selectedTab === 'recycle' }" @click="selectedTab = 'recycle'">분리수거글</button>
              <button :class="{ active: selectedTab === 'bookmark' }" @click="selectedTab = 'bookmark'">🔖 북마크</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <main class="board-table-wrap">
      <table class="board-table">
        <thead>
          <tr>
            <th class="col-num">번호</th>
            <th class="col-category">구분</th>
            <th>제목</th>
            <th class="col-date">작성일</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in filteredPosts" :key="post.id" @click="openDetail(post.id)" class="clickable-row">
            <td>{{ post.seq }}</td>
            <td>
              <span class="category-badge">{{ getCategoryLabel(post.category) }}</span>
            </td>
            <td class="title-cell">
              <div class="title-text">
                <span v-if="post.bookmarked" class="bookmark-flag">🔖</span>
                {{ post.title }}
              </div>
              <div v-if="post.tags?.length" class="tag-list row-tags">
                <button
                  v-for="tag in post.tags"
                  :key="tag"
                  type="button"
                  class="tag-badge clickable-tag"
                  @click.stop="openTagPosts(tag)"
                >
                  #{{ tag }}
                </button>
              </div>
            </td>
            <td>{{ post.displayDate }}</td>
          </tr>
          <tr v-if="filteredPosts.length === 0">
            <td colspan="4" class="empty">작성된 게시글이 없습니다.</td>
          </tr>
        </tbody>
      </table>
    </main>

    <footer class="pagination">
      <button @click="prevPage" :disabled="page === 1">&lt;</button>
      <button v-for="p in totalPages" :key="p" @click="page = p" :class="{ active: p === page }">{{ p }}</button>
      <button @click="nextPage" :disabled="page === totalPages">&gt;</button>
    </footer>

    <div v-if="showFormModal" class="modal-overlay" @click.self="closeFormModal">
      <div class="modal-card" role="dialog" aria-modal="true">
        <h3>{{ formMode === 'create' ? '새 글 작성' : '게시글 수정' }}</h3>

        <label>제목
          <input v-model="form.title" type="text" />
        </label>

        <label>내용
          <textarea v-model="form.content" rows="8"></textarea>
        </label>

        <label>태그
          <input
            v-model="form.tagInput"
            type="text"
            placeholder="태그 입력 후 Enter 또는 Space"
            @keydown.enter.prevent="addTagFromInput"
            @keydown.space.prevent="addTagFromInput"
          />
        </label>

        <div v-if="form.tags.length" class="tag-input-list">
          <span v-for="(tag, idx) in form.tags" :key="tag" class="tag-chip">
            <button type="button" class="tag-remove" @click="removeTag(idx)">✕</button>
            #{{ tag }}
          </span>
        </div>

        <div class="image-actions">
          <button type="button" class="image-upload-button" @click="triggerImageUpload">사진</button>
          <span v-if="form.imageName" class="image-name">{{ form.imageName }}</span>
        </div>

        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          class="hidden-file-input"
          @change="handleImageUpload"
        />

        <img v-if="form.image" :src="form.image" class="image-preview" alt="첨부 이미지 미리보기" />

        <label>게시판
          <select v-model="form.category">
            <option value="festival">축제</option>
            <option value="accommodation">숙박</option>
            <option value="find">찾기</option>
            <option value="free">자유</option>
          </select>
        </label>

        <label>비밀번호 (수정/삭제용)
          <input v-model="form.password" type="password" />
        </label>

        <div class="modal-actions">
          <button @click="submitForm">{{ formMode === 'create' ? '등록' : '저장' }}</button>
          <button class="secondary" @click="closeFormModal">취소</button>
        </div>

        <p class="msg" v-if="formMessage">{{ formMessage }}</p>
      </div>
    </div>

    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-card" role="dialog" aria-modal="true">
        <div class="modal-header">
          <h3 v-if="!detailEditMode">{{ detailPost?.title }}</h3>
          <h3 v-else>게시글 수정</h3>
        </div>

        <template v-if="!detailEditMode">
          <div class="meta">
            <span>작성일 {{ detailPost?.displayDate }}</span>
            <span v-if="detailPost?.updatedAt">수정일 {{ detailPost?.displayUpdatedAt }}</span>
          </div>
          <p class="content-text">{{ detailPost?.content }}</p>

          <img v-if="detailPost?.image" :src="detailPost.image" class="detail-image" alt="첨부 이미지" />

          <div class="vote-row">
            <button
              type="button"
              class="vote like"
              @click="votePost('like')"
              :disabled="Boolean(detailPost?.userVote)"
            >
              👍 추천 {{ detailPost?.likes ?? 0 }}
            </button>

            <button
              type="button"
              class="vote dislike"
              @click="votePost('dislike')"
              :disabled="Boolean(detailPost?.userVote)"
            >
              👎 비추천 {{ detailPost?.dislikes ?? 0 }}
            </button>

            <div v-if="detailPost?.tags?.length" class="tag-list">
              <button
                v-for="tag in detailPost.tags"
                :key="tag"
                type="button"
                class="tag-badge clickable-tag"
                @click="openTagPosts(tag)"
              >
                #{{ tag }}
              </button>
            </div>
          </div>

          <div class="action-row">
            <button class="icon-btn" :class="{ active: detailPost?.likedByMe }" @click="toggleLike(detailPost?.id)">
              ♥ {{ detailPost?.likeCount ?? 0 }}
            </button>

            <button class="icon-btn" :class="{ active: detailPost?.bookmarked }" @click="toggleBookmark(detailPost?.id)">
              🔖 북마크
            </button>

            <button class="icon-btn" @click="attemptShare">
              🔗 공유
            </button>

            <span class="meta-pill">👁 {{ detailPost?.views ?? 0 }}</span>
          </div>

          <p class="msg" v-if="voteMessage">{{ voteMessage }}</p>
          <p class="msg" v-if="shareMessage">{{ shareMessage }}</p>

          <label>비밀번호 확인
            <input v-model="verifyPassword" type="password" placeholder="수정·삭제·공유 비밀번호" />
          </label>

          <div class="modal-actions">
            <button @click="attemptStartEdit">수정</button>
            <button class="danger" @click="attemptDelete">삭제</button>
            <button class="secondary" @click="closeDetailModal">닫기</button>
          </div>
          <p class="msg" v-if="detailMessage">{{ detailMessage }}</p>
        </template>

        <template v-else>
          <h3>게시글 수정</h3>

          <label>제목
            <input v-model="form.title" type="text" />
          </label>

          <label>내용
            <textarea v-model="form.content" rows="8"></textarea>
          </label>

          <label>태그
            <input
              v-model="form.tagInput"
              type="text"
              placeholder="태그 입력 후 Enter 또는 Space"
              @keydown.enter.prevent="addTagFromInput"
              @keydown.space.prevent="addTagFromInput"
            />
          </label>

          <div v-if="form.tags.length" class="tag-input-list">
            <span v-for="(tag, idx) in form.tags" :key="tag" class="tag-chip">
              <button type="button" class="tag-remove" @click="removeTag(idx)">✕</button>
              #{{ tag }}
            </span>
          </div>

          <div class="image-actions">
            <button type="button" class="image-upload-button" @click="triggerImageUpload">사진</button>
            <span v-if="form.imageName" class="image-name">{{ form.imageName }}</span>
          </div>

          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            class="hidden-file-input"
            @change="handleImageUpload"
          />

          <img v-if="form.image" :src="form.image" class="image-preview" alt="첨부 이미지 미리보기" />

          <label>게시판
            <select v-model="form.category">
              <option value="festival">축제</option>
              <option value="accommodation">숙박</option>
              <option value="find">찾기</option>
              <option value="free">자유</option>
            </select>
          </label>

          <label>비밀번호 (현재 비밀번호와 동일하게 입력)
            <input v-model="form.password" type="password" />
          </label>

          <div class="modal-actions">
            <button @click="submitForm">저장</button>
            <button class="secondary" @click="cancelEdit">취소</button>
          </div>
          <p class="msg" v-if="formMessage">{{ formMessage }}</p>
        </template>
      </div>
    </div>

    <div v-if="showTagPostsModal" class="modal-overlay" @click.self="closeTagPostsModal">
      <div class="modal-card" role="dialog" aria-modal="true">
        <div class="tag-posts-header">
          <h3>#{{ selectedTag }} 게시글</h3>
          <button class="secondary" @click="closeTagPostsModal">닫기</button>
        </div>

        <ul v-if="tagPosts.length" class="tag-post-list">
          <li
            v-for="post in tagPosts"
            :key="post.id"
            class="tag-post-item"
            @click="openDetail(post.id); closeTagPostsModal()"
          >
            <div class="tag-post-title">{{ post.title }}</div>
            <div class="tag-post-meta">{{ getCategoryLabel(post.category) }} · {{ post.displayDate }}</div>
          </li>
        </ul>

        <p v-else class="empty">해당 태그가 포함된 게시글이 없습니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import FestivalCalendar from '../components/FestivalCalendar.vue'

const router = useRouter()

function goToMain() {
  router.push('/')
}

const STORAGE_KEY = 'community-posts'
const VOTE_STORAGE_KEY = 'community-votes'

let rawData = null
try {
  rawData = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
} catch (e) {
  console.error('게시글 저장소 파싱 실패:', e)
  rawData = null
}

const RAW = Array.isArray(rawData) ? rawData : []

let voteStorage = {}
try {
  voteStorage = JSON.parse(localStorage.getItem(VOTE_STORAGE_KEY) || '{}')
} catch (e) {
  console.error('투표 저장소 파싱 실패:', e)
  voteStorage = {}
}

const voteMap = ref(voteStorage)

watch(voteMap, (v) => {
  localStorage.setItem(VOTE_STORAGE_KEY, JSON.stringify(v))
}, { deep: true })

const pad2 = (n) => String(n).padStart(2, '0')
const formatDisplay = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${pad2(d.getMonth() + 1)}.${pad2(d.getDate())}`
}

function collectFormTags() {
  const pending = form.value.tagInput.trim().replace(/^#/, '')
  const combined = pending ? [...form.value.tags, pending] : form.value.tags
  return Array.from(new Set(combined.filter(Boolean)))
}

const categoryLabelMap = {
  all: '전체',
  festival: '축제',
  accommodation: '숙박',
  find: '찾기',
  free: '자유'
}

function getCategoryLabel(category) {
  return categoryLabelMap[category] || '자유'
}

const normalizePosts = (posts) =>
  (Array.isArray(posts) ? posts : []).map((p) => ({
    ...p,
    likes: p.likes ?? 0,
    dislikes: p.dislikes ?? 0,
    userVote: p.userVote ?? null,
    views: p.views ?? 0,
    bookmarked: Boolean(p.bookmarked),
    likedByMe: Boolean(p.likedByMe),
    likeCount: p.likeCount ?? 0,
    category: ['festival', 'accommodation', 'find', 'free'].includes(p.category) ? p.category : 'free',
    image: p.image || '',
    imageName: p.imageName || '',
    tags: Array.isArray(p.tags) ? p.tags : []
  }))

const readImageAsDataUrl = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader()
  reader.onload = () => resolve(reader.result)
  reader.onerror = () => reject(reader.error)
  reader.readAsDataURL(file)
})

const rawPosts = ref(
  normalizePosts(RAW).map((p) => ({
    ...p,
    userVote: voteMap.value[p.id] || p.userVote || null
  }))
)

watch(rawPosts, (v) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(v))
}, { deep: true })

const page = ref(1)
const perPage = 10
const query = ref('')
const selectedTab = ref('all')
const selectedCategory = ref('all')

let rotationTimer = null
const todayPopularIndex = ref(0)

const todayPopularPosts = computed(() => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  return rawPosts.value
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

const currentPopularPost = computed(() => {
  return todayPopularPosts.value[todayPopularIndex.value] || null
})

function advanceTodayPopular() {
  if (todayPopularPosts.value.length <= 1) return
  todayPopularIndex.value = (todayPopularIndex.value + 1) % todayPopularPosts.value.length
}

function startTodayPopularRotation() {
  if (rotationTimer) {
    window.clearInterval(rotationTimer)
  }

  if (todayPopularPosts.value.length > 1) {
    rotationTimer = window.setInterval(advanceTodayPopular, 5000)
  }
}

onMounted(() => {
  startTodayPopularRotation()

  const match = window.location.hash.match(/^#\/post\/(\d+)/)
  if (match) {
    const sharedId = Number(match[1])
    if (rawPosts.value.some((post) => post.id === sharedId)) {
      openDetail(sharedId)
    }
  }
})

onBeforeUnmount(() => {
  if (rotationTimer) {
    window.clearInterval(rotationTimer)
    rotationTimer = null
  }
})

watch(todayPopularPosts, () => {
  todayPopularIndex.value = 0
  startTodayPopularRotation()
})

function selectCategory(category) {
  selectedCategory.value = category
}

function isPopularPost(post) {
  const likes = Number(post.likes ?? 0)
  return post.category === 'popular' || likes >= 10
}

function isRecyclePost(post) {
  const likes = Number(post.likes ?? 0)
  const dislikes = Number(post.dislikes ?? 0)
  return post.category === 'recycle' || (dislikes >= 10 && dislikes >= likes + 5)
}

const filteredAll = computed(() => {
  const q = query.value.trim().toLowerCase()

  const items = rawPosts.value
    .slice()
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .map((p, idx) => ({
      ...p,
      seq: rawPosts.value.length - idx,
      displayDate: formatDisplay(p.createdAt),
      displayUpdatedAt: p.updatedAt ? formatDisplay(p.updatedAt) : ''
    }))

  let tabItems = items

  if (selectedTab.value === 'popular') {
    tabItems = items.filter((p) => isPopularPost(p) && !isRecyclePost(p))
  } else if (selectedTab.value === 'recycle') {
    tabItems = items.filter((p) => isRecyclePost(p))
  } else if (selectedTab.value === 'bookmark') {
    tabItems = items.filter((p) => p.bookmarked)
  } else {
    tabItems = items.filter((p) => !isRecyclePost(p))
  }

  const categoryItems =
    selectedCategory.value === 'all'
      ? tabItems
      : tabItems.filter((p) => p.category === selectedCategory.value)

  if (!q) return categoryItems
  return categoryItems.filter((p) => p.title.toLowerCase().includes(q) || p.content.toLowerCase().includes(q))
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredAll.value.length / perPage)))

const filteredPosts = computed(() => {
  page.value = Math.min(page.value, totalPages.value)
  const start = (page.value - 1) * perPage
  return filteredAll.value.slice(start, start + perPage)
})

function applySearch() {
  page.value = 1
}

const showFormModal = ref(false)
const formMode = ref('create')
const form = ref({
  id: null,
  title: '',
  content: '',
  password: '',
  category: 'free',
  image: '',
  imageName: '',
  tags: [],
  tagInput: ''
})
const formMessage = ref('')

const showDetailModal = ref(false)
const detailPostId = ref(null)
const detailEditMode = ref(false)
const verifyPassword = ref('')
const detailMessage = ref('')
const voteMessage = ref('')
const shareMessage = ref('')
const fileInputRef = ref(null)

const showTagPostsModal = ref(false)
const selectedTag = ref('')

const tagPosts = computed(() => {
  if (!selectedTag.value) return []

  return rawPosts.value
    .filter((post) => (post.tags || []).includes(selectedTag.value))
    .slice()
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .map((post) => ({
      ...post,
      displayDate: formatDisplay(post.createdAt)
    }))
})

function openTagPosts(tag) {
  selectedTag.value = tag
  showTagPostsModal.value = true
}

function closeTagPostsModal() {
  showTagPostsModal.value = false
  selectedTag.value = ''
}

function triggerImageUpload() {
  nextTick(() => {
    fileInputRef.value?.click()
  })
}

function handleImageUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return

  readImageAsDataUrl(file).then((dataUrl) => {
    form.value.image = dataUrl
    form.value.imageName = file.name
  })

  event.target.value = ''
}

function openCreateModal() {
  formMode.value = 'create'
  form.value = {
    id: null,
    title: '',
    content: '',
    password: '',
    category: 'free',
    image: '',
    imageName: '',
    tags: [],
    tagInput: ''
  }
  formMessage.value = ''
  showFormModal.value = true
}

function addTagFromInput() {
  const raw = form.value.tagInput.trim().replace(/^#/, '')
  if (raw && !form.value.tags.includes(raw)) {
    form.value.tags.push(raw)
  }
  form.value.tagInput = ''
}

function removeTag(index) {
  form.value.tags.splice(index, 1)
}

function closeFormModal() {
  showFormModal.value = false
  formMessage.value = ''
}

function submitForm() {
  if (!form.value.title.trim() || !form.value.content.trim() || !form.value.password.trim()) {
    formMessage.value = '모든 항목을 입력하세요.'
    return
  }

  if (formMode.value === 'create') {
    const now = new Date()
    const newPost = {
      id: Date.now(),
      title: form.value.title.trim(),
      content: form.value.content.trim(),
      password: form.value.password,
      category: form.value.category || 'free',
      image: form.value.image || '',
      imageName: form.value.imageName || '',
      tags: collectFormTags(),
      createdAt: now.toISOString(),
      updatedAt: '',
      likes: 0,
      dislikes: 0,
      userVote: null
    }
    rawPosts.value.unshift(newPost)
    closeFormModal()
    page.value = 1
    return
  }

  const idx = rawPosts.value.findIndex((p) => p.id === form.value.id)
  if (idx === -1) {
    formMessage.value = '게시글을 찾을 수 없습니다.'
    return
  }

  if (rawPosts.value[idx].password !== form.value.password) {
    formMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  rawPosts.value[idx] = {
    ...rawPosts.value[idx],
    title: form.value.title.trim(),
    content: form.value.content.trim(),
    password: form.value.password,
    category: form.value.category || 'free',
    image: form.value.image || rawPosts.value[idx].image || '',
    imageName: form.value.imageName || rawPosts.value[idx].imageName || '',
    tags: collectFormTags(),
    updatedAt: new Date().toISOString()
  }

  formMessage.value = ''
  detailEditMode.value = false
  showFormModal.value = false
  showDetailModal.value = false
}

function openDetail(id) {
  const idx = rawPosts.value.findIndex((post) => post.id === id)
  if (idx !== -1) {
    rawPosts.value[idx] = {
      ...rawPosts.value[idx],
      views: (rawPosts.value[idx].views ?? 0) + 1
    }
  }

  detailPostId.value = id
  verifyPassword.value = ''
  detailMessage.value = ''
  voteMessage.value = ''
  shareMessage.value = ''
  detailEditMode.value = false
  showDetailModal.value = true
}

function toggleBookmark(postId = detailPost.value?.id) {
  const idx = rawPosts.value.findIndex((post) => post.id === postId)
  if (idx === -1) return

  const current = rawPosts.value[idx]
  rawPosts.value[idx] = {
    ...current,
    bookmarked: !current.bookmarked
  }
}

function toggleLike(postId = detailPost.value?.id) {
  const idx = rawPosts.value.findIndex((post) => post.id === postId)
  if (idx === -1) return

  const current = rawPosts.value[idx]
  const nextLiked = !current.likedByMe

  rawPosts.value[idx] = {
    ...current,
    likedByMe: nextLiked,
    likeCount: Math.max(0, (current.likeCount ?? 0) + (nextLiked ? 1 : -1))
  }
}

function closeDetailModal() {
  showDetailModal.value = false
  detailMessage.value = ''
  voteMessage.value = ''
  shareMessage.value = ''
  verifyPassword.value = ''
  detailEditMode.value = false
  resetOgTags()
}

function attemptStartEdit() {
  if (!verifyPassword.value.trim()) {
    detailMessage.value = '비밀번호를 입력해주세요.'
    return
  }
  const p = detailPost.value
  if (!p) return
  if (p.password !== verifyPassword.value) {
    detailMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  formMode.value = 'edit'
  form.value = {
    id: p.id,
    title: p.title,
    content: p.content,
    password: p.password,
    category: p.category || 'free',
    image: p.image || '',
    imageName: p.imageName || '',
    tags: Array.isArray(p.tags) ? [...p.tags] : [],
    tagInput: ''
  }
  formMessage.value = ''
  detailEditMode.value = true
}

function cancelEdit() {
  detailEditMode.value = false
  formMessage.value = ''
  verifyPassword.value = ''
}

function attemptDelete() {
  if (!verifyPassword.value.trim()) {
    detailMessage.value = '비밀번호를 입력해주세요.'
    return
  }
  const p = detailPost.value
  if (!p) return
  if (p.password !== verifyPassword.value) {
    detailMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  rawPosts.value = rawPosts.value.filter((x) => x.id !== p.id)
  detailPostId.value = null
  showDetailModal.value = false
  verifyPassword.value = ''
}

function votePost(type) {
  const p = detailPost.value
  if (!p) return

  if (voteMap.value[p.id]) {
    voteMessage.value = '이미 투표한 게시글입니다.'
    return
  }

  const idx = rawPosts.value.findIndex((post) => post.id === p.id)
  if (idx === -1) return

  const current = rawPosts.value[idx]
  if (type === 'like') {
    current.likes += 1
  } else {
    current.dislikes += 1
  }
  current.userVote = type

  rawPosts.value[idx] = { ...current }
  voteMap.value[p.id] = type

  if (current.likes >= 10) {
    voteMessage.value = '추천 10회가 되어 인기글 탭에 표시됩니다.'
  } else if (current.dislikes >= 10 && current.dislikes >= current.likes + 5) {
    voteMessage.value = '비추천 10회·추천보다 5개 이상 많아 분리수거글 탭에 표시됩니다.'
  } else {
    voteMessage.value = type === 'like' ? '추천이 등록되었습니다.' : '비추천이 등록되었습니다.'
  }
}

const DEFAULT_TITLE = document.title
const DEFAULT_OG = {
  title: 'LocalHub',
  description: '지역 커뮤니티 게시판 LocalHub',
  url: `${window.location.origin}${window.location.pathname}`
}

function setMetaTag(property, content) {
  let tag = document.querySelector(`meta[property="${property}"]`)
  if (!tag) {
    tag = document.createElement('meta')
    tag.setAttribute('property', property)
    document.head.appendChild(tag)
  }
  tag.setAttribute('content', content)
}

function buildShareUrl(id) {
  return `${window.location.origin}${window.location.pathname}#/post/${id}`
}

function updateOgTags(post, url) {
  document.title = post.title
  setMetaTag('og:title', post.title)
  setMetaTag('og:description', (post.content || '').slice(0, 100))
  setMetaTag('og:url', url)
  if (post.image) {
    setMetaTag('og:image', post.image)
  }
}

function resetOgTags() {
  document.title = DEFAULT_TITLE
  setMetaTag('og:title', DEFAULT_OG.title)
  setMetaTag('og:description', DEFAULT_OG.description)
  setMetaTag('og:url', DEFAULT_OG.url)
}

function copyShareLink(post) {
  const url = buildShareUrl(post.id)
  updateOgTags(post, url)
  navigator.clipboard.writeText(url)
    .then(() => { shareMessage.value = '게시글 링크가 복사되었습니다.' })
    .catch(() => { shareMessage.value = `링크 복사에 실패했습니다: ${url}` })
}

function attemptShare() {
  const p = detailPost.value
  if (!p) return

  if (isPopularPost(p)) {
    copyShareLink(p)
    return
  }
  if (!verifyPassword.value.trim()) {
    shareMessage.value = '내가 쓴 글만 공유할 수 있습니다. 작성 시 등록한 비밀번호를 입력해주세요.'
    return
  }
  if (p.password !== verifyPassword.value) {
    shareMessage.value = '비밀번호가 일치하지 않아 공유할 수 없습니다.'
    return
  }
  copyShareLink(p)
}

function prevPage() {
  if (page.value > 1) page.value--
}

function nextPage() {
  if (page.value < totalPages.value) page.value++
}

const detailPost = computed(() => {
  const post = rawPosts.value.find((p) => p.id === detailPostId.value)
  if (!post) return null
  return {
    ...post,
    userVote: voteMap.value[post.id] || post.userVote || null,
    displayDate: formatDisplay(post.createdAt),
    displayUpdatedAt: post.updatedAt ? formatDisplay(post.updatedAt) : ''
  }
})
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
