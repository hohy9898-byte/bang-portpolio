# 도서 검색 RAG 챗봇

Qwen3 로컬 모델을 사용해, 2026년 10월 기준 총 100개의 도서 정보를 사용해 답변을 리턴합니다.  

## 세팅

- Ollama 를 사용해 다음 두 개의 모델을 받습니다.
  - qwen3-embedding:4b
  - qwen3:4b-instruct-2507-q4_K_M

```bash
ollama pull 모델명
```

- 이후, 해당 프로젝트에 가상환경을 만들고, 패키지를 설치한다.  

```bash
python -m venv venv
source ./venv/Scripts/activate
pip install -r ./requirements.txt
```

- 환경변수를 복사한다.  

```bash
cp -r ./.env.example ./.env
```

- (선택) 알라딘 OpenAPI 로 책 소개와 표지를 받는다. 주제 검색("우주 SF 소설" 등)의 정확도가 크게 올라간다.  
  - [알라딘 TTB](https://www.aladin.co.kr/ttb/wblog_manage.aspx)에서 키를 발급받아 `.env` 에 `ALADIN_TTB_KEY="키"` 추가
  - ISBN 이 다른 책을 가리키는 경우(제목 불일치)는 저장하지 않는다

```bash
python fetch_book_details.py
```

- 벡터 DB를 만든다. 도서 1권을 Document 1개로 저장하며, 다시 실행하면 기존 데이터를 비우고 새로 적재한다.  

```bash
python set_vector_store.py
```

## 구조

- `books.py` : `books.txt` 파싱 (도서 1권 = dict 1개), `book_details.json` 이 있으면 책 소개/표지 병합, 답변에서 도서 제목 찾기
- `fetch_book_details.py` : 알라딘 OpenAPI 로 책 소개, 표지 URL 받기 → `book_details.json`
- `retriever.py` : 하이브리드 검색
  - 벡터 검색: 검색어에 Qwen3-Embedding 용 지시문(`Instruct: ... Query: ...`)을 붙여 검색
  - 키워드 검색: 글자 2개 단위(bigram) BM25. 제목, 저자, "파이썬", "토익" 같은 단어가 그대로 나오는 질문에 강함
  - 두 결과를 순위 기반(RRF)으로 합침
- `set_vector_store.py` : Chroma 벡터 DB 생성
- `main.py` : FastAPI 서버 + 에이전트
  - `filter_books` 툴 : 분류, 저자, 출간연도, 가격 등 정확한 조건 검색
  - `search_books_info` 툴 : 주제, 내용 등으로 하이브리드 검색
  - `session_id` 별로 대화 기록을 메모리에 유지 (서버 재시작 시 초기화)
  - 답변에 나온 보유 도서를 `books` 로 함께 반환 (프론트엔드 도서 카드), 보유 도서에 없는 제목은 서버 로그에 경고

## 실행

FastAPI 기반이므로, uvicorn 으로 실행한다.  

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

- 요청 정보
  - POST : `http://127.0.0.1:8000/api/v1/chat`

- Request Body

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `prompt` | O | 질문 |
| `session_id` | X | 이전 응답의 `session_id`. 보내면 대화가 이어진다 |
| `book_title` | X | 사용자가 보고 있는 도서 제목 (도서 상세 페이지용) |

```json
{
    "prompt": "현재 보유중인 책 중에, 2022년 이후에 출간된 소설은?"
}
```

- Response Body 예시

```json
{
    "answer": "2022년 이후에 출간된 소설 8권:

1. **채식주의자** | 저자: 한강 | 출간일: 2022-03-28
2. **급류** | 저자: 정대건 | 출간일: 2022-09-16
...",
    "session_id": "6f1c2b0e-...",
    "books": [
        {"title": "채식주의자", "author": "한강", "publisher": "창비", "category": "소설/시/희곡", "price": 15000, "pub_date": "2022-03-28", "isbn": "9788936438838", "cover": ""}
    ]
}
```

## 성능 평가

`eval/cases.json` 의 질문 29개로 챗봇 답변을 채점한다. 서버를 띄우지 않고 `main.py` 의 에이전트를 직접 호출한다.

```bash
python eval/run_eval.py --runs 3 --label "변경 내용 메모"
```

- 질문 유형: 조건, 저자, 주제, 후속(대화 2턴), 상세화면(보고 있는 도서 문맥), 일반, 미보유
- 답변에 나온 도서 제목을 보유 도서 100권과 대조해 정답 목록과 비교
  - `all` : 정답 도서를 빠짐없이, 다른 도서 없이 답해야 통과
  - `any` : 정답 도서 중 1권 이상 포함하면 통과 (주제 추천)
  - `none` : 도서를 언급하지 않아야 통과 (일반 대화)
- 4B 모델은 같은 질문에도 답이 달라지므로 `--runs 3` 이상으로 평균을 본다
- 결과는 `eval/results/날짜-시간.json` 에 저장되므로, 개선 전후 파일을 비교한다
- 보유 도서에 없는 제목을 굵게 쓴 답변(지어낸 도서일 가능성)은 따로 집계한다

### 개선 기록 (29문항 x 3회 = 87회)

| 단계 | 통과 | 내용 |
| --- | --- | --- |
| 기준점 | 63/87 (72%) | 도서 1권 = Document 1개, 조건 검색 툴. 실패 대부분은 툴을 부르지 않고 답하거나(저자 질문, "파이썬", "요리책") 지어낸 도서 |
| 하이브리드 검색 | 56/87 (64%) | 검색어 지시문 + BM25. 검색 결과는 일부 좋아졌지만, 툴을 부르지 않는 문제가 그대로라 통과율은 차이 없음(편차 범위) |
| 툴 호출 규칙 | 78/87 (90%) | "도서 질문은 반드시 먼저 툴 호출" 규칙, 결과 개수 10 → 30, 저자 이름 오타 허용 |
| 가격/정렬 설명 | 84/87 (97%) | "가장 비싼" → 정렬, "넘는" → 하한처럼 4B 모델이 헷갈리던 파라미터 설명을 구체화 |

- 남은 실패: "우주를 배경으로 한 SF 소설" (3회). 데이터에 책 소개가 없어 검색으로 찾을 수 없음 → `fetch_book_details.py` 로 책 소개를 받으면 해결 예상
- 배운 점: 4B 모델은 검색 품질보다 툴을 부를지, 파라미터를 어떻게 채울지에서 더 많이 틀린다. 툴 설명에 넣은 예시 숫자("2만원")를 그대로 따라 쓰는 경우도 있었다

## 프론트엔드 연동

`skeleton/chatbot.js`, `skeleton/chatbot.css` 가 우측 하단 챗봇 위젯을 만든다.  
서버를 실행한 뒤 `skeleton/06-main.html` 또는 `skeleton/07-book_detail.html` 을 열고 💬 버튼이나 "도서 검색" 메뉴를 누른다.
