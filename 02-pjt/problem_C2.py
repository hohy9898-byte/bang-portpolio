import os
import requests
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 1. [ 환경 변수 로드 ]
load_dotenv()

MY_TTBKEY = os.getenv('MY_TTBKEY')
ALADIN_SEARCH_URL = 'https://aladin.co.kr/ttb/api/ItemSearch.aspx'
OPENAI_API_KEY = os.getenv('MY_API_KEY')


# 2. OpenAI API 클라이언트 초기화
client = OpenAI(
    base_url='https://gms.ssafy.io/gmsapi/api.openai.com/v1',
    api_key=OPENAI_API_KEY
)


# 3. [ 최대 100개까지 주제별 도서 데이터를 가져오는 함수 정의 ]
def fetch_books_by_topic(topic, max_results=100):
    all_books = []
    page_size = 50  # 알라딘 API는 한 번에 최대 50개까지 응답
    start = 1

    while len(all_books) < max_results:
        remaining = max_results - len(all_books)
        params = {
            'ttbkey': MY_TTBKEY,
            'Query': topic,
            'QueryType': 'Keyword',
            'MaxResults': min(page_size, remaining),
            'start': start,
            'SearchTarget': 'Book',
            'output': 'js',
            'Version': '20131101'
        }
        response = requests.get(ALADIN_SEARCH_URL, params=params).json()
        books = response.get('item', [])
        if not books:
            break

        all_books.extend(books)
        start += 1

    return all_books[:max_results]


# 4. 책 데이터를 ChatGPT로 분류하는 함수 정의 (습관, 시간관리, 독서법, 기타)
CATEGORIES = ['습관', '시간관리', '독서법', '기타']


def classify_books_with_gpt(books):
    # 4.1 [ 분류할 책 제목들을 전달하기 편한 문자열로 취합 ]
    titles_text = "\n".join(f"{i}. {book['title']}" for i, book in enumerate(books, 1))

    # 4.2 [ ChatGPT 대화 메시지 설정 (프롬프트 작성) ]
    # 습관, 시간관리, 독서법, 기타 로 분류
    # (그룹 리스트 형태로 바로 요청하면 응답 생성에 필요한 토큰이 커져
    #  reasoning 모델이 출력 전에 토큰 한도를 소진해버리는 문제가 있어,
    #  가벼운 "번호: 카테고리" 매핑으로 받은 뒤 파이썬에서 그룹핑한다.)
    conversation_history = [
        {"role": "system", "content": (
            "당신은 도서 제목만 보고 카테고리를 분류하는 도서 분류 전문가입니다. "
            "설명 없이 반드시 JSON 객체 하나만 응답합니다."
        )},
        {"role": "user", "content": (
            "아래 번호가 매겨진 도서 제목 목록을 '습관', '시간관리', '독서법', '기타' 중 "
            "하나로 분류해줘.\n"
            '{"번호": "카테고리"} 형태의 JSON 객체 하나로만 응답해줘. '
            "설명이나 코드블록 없이 순수 JSON만 출력해.\n\n"
            f"도서 목록:\n{titles_text}"
        )}
    ]

    # 4.3 [ 생성형 AI에 분류 요청 보내기 ]
    # client.chat.completions.create() 호출 (example 코드 참고)
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=conversation_history,
        max_completion_tokens=16000,
        n=1,
        response_format={"type": "json_object"}
    )

    # 4.4 [ ChatGPT의 응답을 가져와 JSON 으로 추출 ]
    # ! 주의. JSON 형태로 프롬프팅을 하지 못하면 파싱에서 에러가 발생할 수 있습니다.
    content = response.choices[0].message.content
    index_to_category = json.loads(content)  # 응답에서 JSON 데이터를 추출하고 파싱

    # 번호 -> 카테고리 매핑을 카테고리 -> 제목 리스트 형태로 재구성
    classification = {category: [] for category in CATEGORIES}
    for i, book in enumerate(books, 1):
        category = index_to_category.get(str(i), '기타')
        if category not in classification:
            category = '기타'
        classification[category].append(book['title'])

    return classification   # 분류 정보 반환


# 5. [ 데이터를 JSON 파일로 저장하는 함수 정의 ]
def save_to_json(data, filename):
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 6. '독서' 도서 데이터를 처리하는 함수 정의
def process_reading_books():
    # 6.1 [ '독서'와 관련된 도서 검색 (100개) ]
    books = fetch_books_by_topic('독서', max_results=100)  # fetch_books_by_topic() 호출

    # 6.2 [ 생성형 AI를 이용해 책 분류 ]
    classification = classify_books_with_gpt(books)  # classify_books_with_gpt() 호출

    # 6.3 [ 분류된 책 정보를 JSON 파일로 저장 ]
    # output/reading_habits.json 으로 저장하기
    save_to_json(classification, 'reading_habits.json')  # save_to_json() 호출

    # 완료 메시지 출력
    print("'output/reading_habits.json' 파일이 생성되었습니다.")


# 함수 실행
if __name__ == '__main__':
    process_reading_books()
