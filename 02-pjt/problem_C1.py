import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# 1. [ 환경 변수 로드 ]
load_dotenv()

MY_TTBKEY = os.getenv('MY_TTBKEY')
ALADIN_SEARCH_URL = 'https://aladin.co.kr/ttb/api/ItemSearch.aspx'


# 2. [ 최대 100개까지 주제별 도서 데이터를 가져오는 함수 정의 ]
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


# 3. '인공지능' 도서 데이터를 처리하는 함수 정의
def process_ai_books():
    # 3.1 [ '인공지능' 관련 도서 검색 ]
    # fetch_books_by_topic()을 호출하여 '인공지능' 관련 도서를 100개 수집합니다.
    books = fetch_books_by_topic('인공지능', max_results=100)

    # 3.2 [ 수집된 데이터에서 가격 정보가 있는 책 필터링 및 가격순 정렬 ]
    priced_books = [book for book in books if book.get('priceStandard')]
    sorted_books = sorted(priced_books, key=lambda book: book['priceStandard'], reverse=True)

    # 3.3 [ 상위 10개 도서 선택 ]
    top10_books = sorted_books[:10]

    # 3.4 [ 상위 10개 도서 정보 출력 ]
    print("가격이 높은 순서대로 상위 10개 도서:")
    for i, book in enumerate(top10_books, 1):
        print(f"{i}. 제목: {book['title']}, 가격: {book['priceStandard']}원")

    # 3.5 [ JSON 파일로 저장할 데이터 준비 ]
    # output/ai_top10_books.json 파일로 저장
    summary = [{'title': book['title'], 'author': book.get('author')} for book in top10_books]

    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / 'ai_top10_books.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 3.6 [ 완료 메시지를 출력 ]
    print("'ai_top10_books.json' 파일이 생성되었습니다.")

# 함수 실행
if __name__ == '__main__':
    process_ai_books()
