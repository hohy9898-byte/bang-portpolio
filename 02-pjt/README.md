# 02-PJT : API 요청을 통한 데이터 수집과 생성형 AI 데이터 분류, TTS 변환

AI 기반 도서 분석과 창작 지원 통합 솔루션 서비스 - 2회차 관통 프로젝트

- 진행일자 : 2026.09.04
- 구현 과제 그룹 : **B (다양한 주제 데이터 수집 및 통합)**, **C (데이터 검색 기능 확장 및 분석)**

## 목차
- [구현 환경](#구현-환경)
- [실행 방법](#실행-방법)
- [구현 내용](#구현-내용)
- [학습 내용 및 느낀 점](#학습-내용-및-느낀-점)

## 구현 환경
- Python 3.11+
- 알라딘(Aladin) 상품 검색 API
- SSAFY GMS OpenAI 호환 게이트웨이 (`https://gms.ssafy.io/gmsapi/api.openai.com/v1`, 모델 `gpt-5-nano`)
- 사용 라이브러리 : `requests`, `python-dotenv`, `gTTS`, `openai`

## 실행 방법
1. `.env.example`을 복사해 `.env`로 이름을 바꾸고 발급받은 키를 채운다.
   ```
   MY_TTBKEY='알라딘에서 발급받은 TTBKey'
   MY_API_KEY='SSAFY GMS에서 발급받은 API 키'
   ```
2. 의존성 설치
   ```
   pip install -r requirements.txt
   ```
3. 문제별 스크립트 실행
   ```
   python problem_B1.py
   python problem_B2.py
   python problem_B3.py
   python problem_C1.py
   python problem_C2.py
   python problem_C3.py
   ```
4. 실행 결과물은 `output/` 폴더에 생성된다.

## 구현 내용

### problem_B1.py — 주제별 도서 데이터 수집 및 통계 (F207, F208)
- `fetch_books_by_topic(topic, max_results)` : 알라딘 API에 `Query=topic`, `QueryType='Keyword'`로 요청을 보내 도서 목록(JSON)을 반환
- `collect_and_analyze_books()` : `자연`, `예술`, `기술` 세 주제에 대해 각 30권씩 조회한 뒤, 주제별/전체 평균 가격(`priceStandard`)과 평균 출판 연도(`pubDate` 앞 4자리)를 계산해 출력

**실행 결과 예시**
```
통합된 도서 수: 90

전체 통계: 평균 가격 20816원, 평균 출판 연도 2022
자연 주제 통계:
  평균 가격: 19660.00원
  평균 출판 연도: 2022
예술 주제 통계:
  평균 가격: 22796.67원
  평균 출판 연도: 2020
기술 주제 통계:
  평균 가격: 19990.00원
  평균 출판 연도: 2023
```

### problem_B2.py — 할인/정가 도서 분류 및 저장 (F209)
- `classify_and_save_books()` : `fetch_books_by_topic`을 재사용해 '경제' 도서 50권을 조회
- 할인가(`priceSales`)가 정가(`priceStandard`)보다 낮으면 할인 도서, 아니면 정가 도서로 분류
- 결과를 각각 `output/discounted_books.json`, `output/regular_priced_books.json`으로 저장

**실행 결과 예시**
```
할인 중인 책 48개, 정가인 책 2개를 저장했습니다.
```

### problem_B3.py — 한국문학 도서 요약 TTS 변환 (F210)
- `save_books_to_json(books, filename, max_save=5)` : `description`이 존재하는 도서만 최대 5개 골라 `{"제목": ..., "요약": ...}` 형태의 JSON으로 저장
- `create_tts_file(text, filename)` : gTTS로 텍스트를 mp3 파일로 변환
- `process_korean_literature_books()` : '한국문학' 주제로 도서를 조회 → 5개 선별/저장 → 각 도서의 제목+요약을 결합해 `output/book_1.mp3` ~ `book_5.mp3`로 저장

**실행 결과 예시**
```
5개의 책 정보를 처리하고 음성 파일로 저장했습니다.
```

### problem_C1.py — 검색 결과 페이지네이션 및 가격순 정렬 (F211~F213)
- `fetch_books_by_topic(topic, max_results=100)` : 알라딘 API가 한 번에 최대 50개만 응답하는 제약을 극복하기 위해, `start`(페이지 번호)를 늘려가며 여러 번 요청해 원하는 개수만큼 누적 수집
- `process_ai_books()` : '인공지능' 도서 100권을 수집 → 정가(`priceStandard`) 기준 내림차순 정렬 → 상위 10권의 제목/저자만 `output/ai_top10_books.json`으로 저장

**실행 결과 예시**
```
가격이 높은 순서대로 상위 10개 도서:
1. 제목: the AI GRAPHICS : 인공지능, 캐릭터..., 가격: 70000원
...
'ai_top10_books.json' 파일이 생성되었습니다.
```

### problem_C2.py — 생성형 AI 기반 도서 분류 (F214~F215)
- `fetch_books_by_topic()` : C1과 동일한 페이지네이션 함수로 '독서' 도서 100권 수집
- `classify_books_with_gpt(books)` : GPT(`gpt-5-nano`)에게 각 도서를 '습관', '시간관리', '독서법', '기타'로 분류하도록 요청, `response_format={"type": "json_object"}`로 JSON 응답을 강제
- `process_reading_books()` : 분류 결과를 `output/reading_habits.json`으로 저장

**실행 결과 예시**
```
'output/reading_habits.json' 파일이 생성되었습니다.
```

### problem_C3.py — 주제별 도서 정보 TTS 변환 (F216~F217)
- `save_books_info(books, filename)` : '음악' 도서 10권의 제목/저자/소개를 `output/music_books_info.txt`로 저장
- `create_audio_file(text_file, audio_file)` : 저장된 텍스트 파일을 읽어 gTTS로 `output/music_books.mp3` 생성

**실행 결과 예시**
```
output/music_books_info.txt 파일이 생성되었습니다.
output/music_books.mp3 파일이 생성되었습니다.
모든 작업이 완료되었습니다.
```

## 학습 내용 및 느낀 점

### 학습한 내용
- `.env` + `python-dotenv`로 API 키 등 민감 정보를 코드에서 분리해 관리하는 방법을 익혔다.
- 알라딘 API의 `QueryType`(Keyword/Title/Author 등), `MaxResults`, `start` 같은 파라미터의 역할과, 응답 JSON의 `item` 배열 구조(`priceStandard`, `priceSales`, `pubDate`, `description` 등 필드)를 이해했다.
- 여러 주제를 순회하며 데이터를 누적 수집하고, 주제별 통계와 전체 통계를 동시에 구하는 로직(리스트 누적 + 평균 계산)을 구현했다.
- `pathlib.Path`로 `output` 폴더를 생성할 때 `mkdir(exist_ok=True)`를 사용하면 폴더가 이미 있어도 에러 없이 넘어간다는 점을 배웠다.
- `gTTS`를 이용해 텍스트를 음성 파일로 변환하는 기본 흐름(`gTTS(text=..., lang='ko').save(path)`)을 익혔다.
- 알라딘 API가 한 번의 요청당 최대 50건만 반환한다는 제약을, `start`(페이지 번호)를 증가시키며 반복 요청·누적하는 방식으로 우회하는 페이지네이션 패턴을 익혔다.
- OpenAI SDK로 SSAFY GMS 게이트웨이(`base_url` 커스텀)를 호출하는 법과, `response_format={"type": "json_object"}`로 JSON 형태의 응답을 강제하는 방법을 익혔다.

### 어려웠던 부분
- 알라딘 API 문서에서 어떤 `QueryType`을 써야 주제 기반 검색이 되는지 처음엔 헷갈렸다. 도서 제목이나 저자가 아닌 '자연', '예술' 같은 주제어이기 때문에 `Keyword` 타입이 적합하다는 것을 문서를 다시 보고 확인했다.
- `pubDate`가 문자열(`"2025-06-27"`)로 오기 때문에 연도만 추출해 정수로 변환하는 과정에서, 값이 비어있거나 형식이 다른 경우를 고려해 `isdigit()` 체크가 필요했다.
- 로컬 환경에 `gTTS`가 설치되어 있지 않아 `requirements.txt` 기준으로 재설치했는데, 이 과정에서 기존에 설치돼 있던 `openai` 등 패키지 버전이 낮아지며 의존성 충돌 경고가 발생했다. 프로젝트별로 가상환경(venv)을 분리하지 않으면 이런 충돌이 생길 수 있다는 것을 체감했다.
- GitLab 원격 저장소의 `master` 브랜치가 protected 상태라 히스토리를 정리하는 과정(force push)이 막혀서, 병합 커밋(`merge -s ours` + tree 교체)으로 우회해 일반 push로 반영했다.
- `gpt-5-nano` 모델은 `temperature`/`top_p`를 기본값(1) 외의 값으로 지정하면 400 에러가 발생해, 두 파라미터를 아예 제거해야 했다.
- 도서 100권을 '카테고리 → 제목 리스트' 형태의 JSON으로 한 번에 분류해달라고 요청하니, reasoning 토큰이 `max_completion_tokens`(16000)를 전부 소진해버려 실제 응답 내용이 빈 문자열로 오는 문제를 겪었다. `usage.completion_tokens_details.reasoning_tokens` 값을 확인해 원인을 찾았고, '번호 → 카테고리'라는 훨씬 가벼운 매핑 형태로 요청을 바꾼 뒤 파이썬에서 그룹으로 재구성하는 방식으로 해결했다.

### 느낀 점
API 문서를 직접 읽고 필요한 파라미터를 찾아 요청을 구성하는 경험을 통해, 단순히 라이브러리 사용법을 아는 것과 실제 서비스에 맞게 데이터를 가공하는 것은 다른 문제라는 걸 느꼈다. 특히 통계 계산처럼 간단해 보이는 로직도 실제 API 응답의 결측값·형식을 고려하지 않으면 쉽게 오류가 난다는 점을 다시 확인할 수 있었다.
