import json  # JSON 파일을 처리하기 위한 라이브러리
from pathlib import Path  # 파일 경로를 처리하기 위한 라이브러리

# 카테고리 데이터를 뽑아 JSON파일로 만들기
# 아래에 생성형 AI를 활용한 코드 작성

# 1. 파일 경로 설정 (books_2000.json 사용)
file_path = Path('./skeleton/data/books_2000.json')  # 파일 경로 설정 부분

# 파일 존재 여부 확인
if file_path.exists():  # 파일이 존재할 경우
    # 2. 파일 열기
    with file_path.open(encoding='utf-8') as f:
        books = json.load(f)  # 파일을 열고 JSON 데이터를 읽은 뒤 Python dictionary로 변환

    # 3. categoryId, categoryName 기준으로 도서 정보 분류
    category_books = {}  # 카테고리별 도서 정보를 저장할 딕셔너리
    for book in books:
        category_id = str(book['categoryId'])
        category_name = book['categoryName']

        if category_id not in category_books:
            category_books[category_id] = {
                'name': category_name,
                'books': [],
            }

        category_books[category_id]['books'].append({
            'title': book['title'],
            'author': book['author'],
            'publisher': book['publisher'],
            'pubDate': book['pubDate'],
            'isbn': book['isbn13'],
            'price': book['priceSales'],
        })

    # 4. 카테고리별 도서 정보를 담은 새로운 JSON 파일 생성
    output_path = Path('./skeleton/data/category_books.json')
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(category_books, f, ensure_ascii=False, indent=2)

    print(f"JSON 파일이 생성되었습니다: {output_path.name}")
else:
    print(f"파일이 존재하지 않습니다: {file_path}")
