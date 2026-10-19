# PJT 03 - 반응형 웹 페이지 구성

AI 기반 도서 분석과 창작 지원 통합 솔루션 서비스 **ThRead**의 메인 페이지와 도서 상세 페이지를
HTML, CSS, Bootstrap 5.3으로 구현했습니다.

## 개발 환경

- HTML, CSS
- Bootstrap 5.3.3, Bootstrap Icons 1.11.3
- Visual Studio Code, Google Chrome

## 파일 구성

| 파일 | 요구사항 | 내용 |
| --- | --- | --- |
| `01-navbar.html` | F301, F302 | Navbar & Hero |
| `02-bestseller.html` | F303 | 베스트셀러 (Carousel) |
| `03-ai_recommendation.html` | F304 | AI 추천 (Grid System) |
| `04-genre_list.html` | F305 | 장르별 도서 목록 (Flexbox) |
| `05-popular_thread.html` | F306 | 인기 쓰레드 (Card, Pagination) |
| `06-main.html` | F307 ~ F311 | 메인 페이지 최종본 (결합, 로그아웃 Modal, 베스트셀러 오버랩, 장르 Grid) |
| `04-genre_list_grid.html` | F310 | 장르별 도서 목록 (CSS Grid) |
| `07-book_detail.html` | F311 | 도서 상세 페이지 (채식주의자) |
| `08-integrated.html` | F301 ~ F311 | 01 ~ 07 통합본 (메인 / 도서 상세 화면 전환 + AI 챗봇) |
| `chatbot.js`, `chatbot.css` | - | AI 도서 추천 챗봇 위젯 (`261015-local-model` 서버 연동) |

## 단계별 구현 내용

### 1. Navbar & Hero (F301, F302)

- `navbar-expand-sm`으로 576px 미만에서 토글 메뉴로 전환
- `position-absolute`와 `z-index: 1000`으로 Hero 위에 투명한 Navbar 배치
- 로고는 `Th`와 `Read`를 각각 `<span>`으로 나누어 색상 지정
- `<br class="d-sm-none">`으로 576px 미만에서만 Hero 제목 줄바꿈

<!-- 캡처: 576px 이상 / 576px 미만 -->

### 2. Bestseller (F303)

- Carousel 슬라이드 3개에 도서 4권씩, 총 12권 배치
- `data-bs-ride="carousel"`로 자동 전환, Next 컨트롤만 출력
- 이미지는 `width: 150px; height: 220px; object-fit: cover`로 크기 고정

<!-- 캡처 -->

### 3. AI Recommendation (F304)

- `.row align-items-center` 안에 `col-md-7`과 `col-md-5`로 7:5 비율 구성
- "활동 데이터 기반"에 `.highlight` 클래스로 색상, 글꼴, 크기 강조

<!-- 캡처 -->

### 4. Genre List (F305)

- `display: flex; flex-wrap: wrap`으로 컨테이너 구성
- `flex: 0 0 calc((100% - 3rem) / 4)`로 아이템을 4열, 고정 크기로 배치
- 장르명은 `position: absolute`로 이미지 좌측 하단에 오버레이
- 576px 미만에서 `flex-basis: 100%`로 1열 배치

<!-- 캡처: 576px 이상 / 576px 미만 -->

### 5. Popular Thread (F306)

- Card 컴포넌트에 `h-100`을 적용해 같은 행의 카드 높이를 맞추고, footer가 항상 카드 하단에 위치하도록 구성
- `col-12 col-sm-4`로 3열 / 1열 반응형 배치
- Pagination은 `.thread .pagination .page-link` 선택자로 Bootstrap보다 높은 명시도를 주어 테두리 제거, 활성 페이지 색상 지정

<!-- 캡처: 576px 이상 / 576px 미만 -->

### 6. 메인 페이지 결합 & 로그아웃 Modal (F307, F308)

- 01 ~ 05의 섹션과 스타일을 하나의 `06-main.html`로 결합
- 로그아웃 메뉴에 `data-bs-toggle="modal"`을 연결해 확인 창 표시
- 닫기(X), 취소, 로그아웃 버튼에 `data-bs-dismiss="modal"`을 적용하고, Modal 바깥 영역을 클릭해도 닫히도록 구성

<!-- 캡처: 메인 페이지 전체 / Modal -->

### 7. 심화 - 베스트셀러 오버랩 (F309)

- 베스트셀러 섹션에 `margin-top: -150px`과 `z-index`를 주어 Hero 위에 절반만 걸치도록 배치
- Hero에는 `padding-bottom`을 주어 제목이 가려지지 않게 조정하고, AI 추천 섹션의 상단 간격 축소

<!-- 캡처 -->

### 8. 심화 - Genre List CSS Grid (F310)

- `grid-template-columns: repeat(8, 1fr)`, `grid-auto-rows: 120px`으로 8열 격자 구성
- `grid-column`, `grid-row`의 `span` 값으로 아이템마다 다른 크기와 위치 지정
- 576px ~ 991px에서는 4열 x 4행으로 재배치
- 576px 미만에서는 1열로 바꾸고 위치 지정을 `auto`로 해제
- `06-main.html`의 장르 섹션에도 같은 Grid 레이아웃 적용

<!-- 캡처: 576px 이상 / 576px 미만 -->

### 9. 심화 - 도서 상세 페이지 (F311)

- `min-height: 100vh` Hero에 도서 표지를 배경으로 깔고, `linear-gradient`로 좌측은 어둡고 우측은 투명한 오버레이 적용
- 좌측에 제목, archive 아이콘이 들어간 "담기" 버튼, 도서 및 작가 소개 배치
- 우측에 `nav-tabs`로 "대여 가능 도서관"(Google Map iframe), "쓰레드"(목록, Pagination, 쓰레드 작성 버튼) 탭 구성
- 메인 페이지 베스트셀러의 "채식주의자"를 클릭하면 상세 페이지로 이동
- 명세서의 `assets/book_detail/book_cover.jpg`가 제공되지 않아, 현재는 베스트셀러 표지(`assets/bestsellers/img2.jpeg`)를 임시 배경으로 사용 중

<!-- 캡처: 576px 이상 / 576px 미만 -->

### 10. 추가 - 통합 페이지 + AI 챗봇 (08)

- 01 ~ 07을 `08-integrated.html` 한 파일로 합치고, URL hash로 화면을 전환
  - `#home`(기본): 메인 화면 (Hero, 베스트셀러, AI 추천, 장르, 쓰레드)
  - `#book-detail`: 도서 상세 화면 (베스트셀러의 "채식주의자" 클릭 시)
  - `hashchange` 이벤트에서 두 `<main>`에 `d-none`을 번갈아 적용
- Navbar, 로그아웃 Modal, 챗봇은 두 화면이 하나씩만 두고 공유
- AI 챗봇 위젯(`chatbot.js`, `chatbot.css`)
  - 우측 하단 버튼, Navbar의 "도서 검색", AI 추천 섹션의 "AI에게 추천받기" 버튼으로 Offcanvas 채팅창 열기
  - 상세 화면에서는 보고 있는 도서(`data-book-title`)를 함께 전송해 "비슷한 책 추천" 등에 활용
  - 답변(마크다운)은 marked로 변환하고 DOMPurify로 정제해 출력
  - 답변에 나온 도서를 표지 카드(제목, 저자, 가격)로 표시하고, "채식주의자" 카드는 상세 화면으로 이동
  - 백엔드는 `../261015-local-model` 참고 ([README](../261015-local-model/README.md))

<!-- 캡처: 메인 화면 / 상세 화면 / 챗봇 -->

## 어려웠던 점과 해결 과정

### 1. 폰트가 적용되지 않는 문제

- **문제**: `@font-face`로 폰트를 정의했는데 화면에 적용되지 않음
- **원인**: 스켈레톤 코드의 `format("ttf")`는 유효한 값이 아니어서 브라우저가 해당 폰트를 무시함
- **해결**: TTF 파일의 올바른 형식 이름인 `format("truetype")`으로 수정

### 2. 섹션을 결합하자 스타일이 깨지는 문제

- **문제**: 01 ~ 05 파일을 `06-main.html`로 합치자 일부 섹션 제목의 크기와 여백이 달라짐
- **원인**: 03 파일의 `.section-title`이 전역 선택자여서 다른 섹션 제목에도 적용됨. 또한 03 파일만 폰트 이름이 `SBAggroOTF_L`이고 나머지는 `SBAggro_L`이었음
- **해결**: `.section-title`을 공통 스타일로 정리하고 섹션별 차이는 `.bestseller .section-title`처럼 범위를 좁혀 덮어씀. 폰트 이름은 `SBAggro_L`로 통일

### 3. Pagination 스타일이 바뀌지 않는 문제

- **문제**: `.page-link`에 테두리 제거, 색상 지정을 했지만 적용되지 않음
- **원인**: Bootstrap에 정의된 스타일과 명시도가 같거나 더 높아서 덮어쓰지 못함
- **해결**: `.thread .pagination .page-link`처럼 부모 선택자를 붙여 명시도를 높임

### 4. 페이지 번호를 누르면 맨 위로 이동하는 문제

- **문제**: Pagination 번호나 메뉴를 클릭하면 페이지 최상단으로 스크롤됨
- **원인**: `href="#"`는 "문서 맨 위"를 가리키는 앵커이기 때문
- **해결**: 이동할 페이지가 없는 링크(도서 검색, 마이 페이지, 페이지 번호, 쓰레드 작성)는 `href="javascript:void(0)"`로 변경 (`06-main.html`, `07-book_detail.html`)
  - 로고는 홈으로 가는 링크이므로 메인 페이지 파일로 연결
  - 섹션으로 이동해야 하는 링크는 `id`를 지정해 `href="#thread"`처럼 연결
- **예외**: 로그아웃 링크는 `href="#"`를 그대로 둠. Bootstrap은 `data-bs-toggle="modal"`이 붙은 `<a>` 태그를 클릭하면 기본 동작을 자체적으로 막기 때문에 맨 위로 이동하지 않음

### 5. 섹션 폭 80%가 적용되지 않는 문제

- **문제**: 쓰레드 목록에 폭 80%를 주었지만 의도한 대로 보이지 않음
- **원인**: Bootstrap `.container`가 화면 크기별 `max-width`를 가지고 있어 충돌함
- **해결**: `.container` 대신 별도 클래스(`.thread-list`)를 만들어 `width: 80%; margin: 0 auto` 적용

### 6. 베스트셀러 오버랩의 반응형 처리 (F309)

- **문제**: 음수 `margin-top`으로 Hero 위에 겹쳤더니, 모바일에서 Hero 제목을 가림
- **원인**: 모바일에서는 도서가 2x2로 배치되어 카드 높이가 약 2배로 늘어남
- **해결**: 768px 미만에서는 겹치는 값을 80px로 줄이는 미디어 쿼리 추가

### 7. Flexbox와 CSS Grid의 차이 (F305, F310)

- Flexbox는 한 방향으로 아이템을 흘려 배치하기 때문에 모든 아이템의 크기가 같은 목록에 적합함
- CSS Grid는 행과 열의 위치를 직접 지정할 수 있어, 아이템마다 크기가 다른 레이아웃에 적합함
- Grid 버전에서는 위치를 CSS로 지정했기 때문에 HTML 순서를 바꾸지 않아도 되었고, 모바일에서는 HTML 순서대로 쌓이도록 할 수 있었음

### 8. 필수 결과물을 유지하면서 심화 과제 적용하기 (F310)

- **문제**: F310은 "기존 04-genre_list.html을 확장"하는 과제인데, 원본을 수정하면 필수 과제 F305(Flexbox)의 결과물이 사라짐
- **해결**: 원본 `04-genre_list.html`은 그대로 두고, `04-genre_list_grid.html`을 새로 만들어 CSS Grid로 구현
  - 메인 페이지 `06-main.html`은 심화까지 모두 적용한 최종본이므로 장르 섹션을 Grid 버전으로 교체
- 이렇게 하여 필수(Flexbox)와 심화(Grid) 결과를 나란히 비교할 수 있음

### 9. 태블릿 구간에서 Grid 칸이 너무 작아지는 문제 (F310)

- **문제**: 8열 Grid는 576px ~ 991px 구간에서 한 칸의 폭이 너무 좁아져 이미지가 잘 보이지 않음
- **해결**: `@media (min-width: 576px) and (max-width: 991.98px)` 구간에서 4열 x 4행으로 재배치하고, 10개 아이템이 빈칸이나 겹침 없이 16칸을 채우도록 `grid-column`/`grid-row`를 다시 지정

### 10. container와 row를 한 요소에 같이 쓴 구조 (F303, F309)

- **문제**: 베스트셀러 섹션을 `<div class="container row ...">`처럼 한 요소에 작성했는데, Bootstrap 권장 구조는 `container > row` 중첩임
- **원인**: `.row`는 col의 안쪽 여백을 상쇄하기 위해 좌우에 음수 margin을 가지는데, 같은 요소에 `.container`의 margin(가운데 정렬)과 겹쳐 `mx-auto`로 억지로 덮어쓰고 있었음
- **해결**: `container > row`로 중첩 구조를 바꿈. 이때 row의 음수 margin 때문에 내용이 바깥쪽으로 12px 넓어지므로, 바깥 container의 안쪽 여백을 `px-4`(24px)로 늘려 기존과 같은 여백을 유지함
  - 기존: container padding 12px + col padding 12px = 24px
  - 변경: container padding 24px − row margin 12px + col padding 12px = 24px

### 11. 통합 시 클래스 이름 충돌 (08)

- **문제**: 06과 07의 스타일을 그대로 합치면 베스트셀러 아래의 작은 도서명 캡션이 4rem 크기로 커짐
- **원인**: `.book-title`이 06에서는 0.8rem 회색 캡션, 07에서는 4rem 상세 제목으로 같은 이름을 다른 용도로 쓰고 있었음
- **해결**: 상세 제목을 `.detail-title`로 이름을 분리함. 또한 07의 `body`에 주던 어두운 배경과 흰 글자를 상세 화면 `.detail-view`에만 적용

### 12. 도서 상세를 Modal이 아닌 화면 전환으로 만든 이유 (08)

- **처음 생각**: 상세 페이지를 전체 화면 Modal(`modal-fullscreen`)로 띄우면 HTML만으로 간단히 구현 가능
- **문제**: Bootstrap Modal은 열려 있는 동안 포커스를 Modal 안에 가두기 때문에(focus trap), 그 위에 챗봇 Offcanvas를 열어도 입력창에 글자를 입력할 수 없음
- **해결**: 상세 화면을 별도 `<main>`으로 두고 URL hash로 메인/상세를 전환함. 주소에 `#book-detail`이 남으므로 새로고침하거나 링크를 공유해도 상세 화면이 그대로 열리는 장점도 있음

### 13. 숨겨진 섹션으로 이동하지 않는 문제 (08)

- **문제**: 상세 화면에서 Navbar의 "쓰레드"(`#thread`)를 누르면 메인 화면은 나타나지만 쓰레드 섹션으로 스크롤되지 않음
- **원인**: 브라우저는 hash가 바뀌는 순간 해당 요소로 스크롤하는데, 그 시점에는 메인 화면이 `d-none`으로 숨겨져 있어 이동할 위치가 없음
- **해결**: `hashchange`에서 메인 화면을 먼저 보이게 한 뒤, `scrollIntoView()`로 직접 해당 섹션으로 이동

### 14. 장르 섹션은 Grid 버전만 사용 (08)

- F305(Flexbox)와 F310(CSS Grid)은 같은 섹션의 필수/심화 결과물이므로, 통합본에는 심화 결과인 Grid 버전만 넣음
- Flexbox 버전은 `04-genre_list.html`에 그대로 남아 있어 비교 가능

### 15. 챗봇이 책을 지어내거나 "없다"고 답하는 문제 (챗봇)

- **문제**: 질문 29개로 만든 평가셋(3회 반복)으로 채점해 보니 통과율 72%. 유발 하라리의 책 제목을 지어내거나, 보유 중인 파이썬 책을 "없다"고 답함
- **원인 찾기**: 처음에는 검색이 부정확하다고 보고 하이브리드 검색(벡터 + 키워드)을 적용했지만 통과율이 오르지 않음(64%). 실패한 답변을 다시 보니 대부분 4B 모델이 **검색 툴을 아예 부르지 않고** 기억으로 답한 경우였음
- **해결**
  - 시스템 프롬프트에 "도서 질문은 반드시 먼저 툴 호출", "툴 결과에 없는 도서는 지어내지 않음" 규칙 추가
  - 모델이 저자 이름을 "헤르ман 헤세"처럼 오타 내도 찾도록 비슷한 이름까지 허용
  - "가장 비싼" → 정렬, "2만원 넘는" → 가격 하한처럼 헷갈리던 파라미터 설명을 구체화
  - 결과: 72% → 90% → **97%** (남은 실패는 책 소개 데이터가 없어 생기는 "우주 SF 소설" 1문항)
- **주의할 점**: 툴 설명에 예시로 적은 "2만원"을 모델이 그대로 따라 써서, "가장 비싼 책" 질문에 없는 가격 조건을 넣은 적이 있음. 작은 모델에게는 예시 하나도 조심해서 넣어야 함
- 자세한 개선 기록은 [백엔드 README](../261015-local-model/README.md)의 "개선 기록" 참고

## 새로 배운 것

- Bootstrap 브레이크포인트(`sm` 576px, `md` 768px)와 반응형 유틸리티 클래스(`d-sm-none`, `col-sm-4` 등)
- CSS 명시도와 Bootstrap 스타일을 덮어쓰는 방법
- `object-fit: cover`로 이미지 비율을 유지하며 영역 채우기
- `position: absolute`와 `z-index`를 이용한 오버레이, 섹션 겹치기
- Bootstrap Carousel, Modal, nav-tabs 등 JS 컴포넌트를 `data-bs-*` 속성만으로 사용하는 방법
- Flex 컨테이너에 `gap`을 주면 자식마다 margin을 따로 주지 않아도 간격을 한 번에 관리할 수 있고, 가로/세로 방향이 바뀌어도 같은 간격이 유지됨
- 제목이 아닌 설명 문구는 `<h3>` 대신 `<p>`를 쓰는 시맨틱 마크업. 제목 태그는 문서 구조(개요)를 나타내므로 스타일 목적으로 쓰지 않음
- 챗봇 성능을 몇 개 질문으로 감으로 판단하지 않고, 정답이 있는 평가셋을 만들어 개선 전후를 숫자로 비교하는 방법
- 작은 LLM(4B)은 검색 품질보다 **툴을 언제 부르고 파라미터를 어떻게 채우는지**에서 더 많이 틀린다는 것. 원인을 확인하기 전에 고치면 효과 없는 작업을 하게 됨

## 느낀 점
방호준 : 사람의 명령수행 능력보다 ai의 능력이 더 뛰어나다는 것을 느꼈다. 앞으로 해야할 일은 ai가 짠 코드를 이해하여 정확한 명령을 내릴수 있는 능력을 키우는 일이라고 생각한다.
<!-- 직접 작성 -->
