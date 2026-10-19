from datetime import datetime  # 날짜와 시간을 처리하기 위한 라이브러리
import json  # JSON 파일을 처리하기 위한 라이브러리
from pathlib import Path  # 파일 경로를 처리하기 위한 라이브러리

# 월별 책 정보 모아보고 평균 가격 계산하기
# 아래에 전체 코드 작성

# 1. 파일 경로 설정 (books_2000.json 사용)
file_path = Path('./skeleton/data/books_2000.json')  # 파일 경로 설정 부분

# 파일 존재 여부 확인
if file_path.exists():  # 파일이 존재할 경우
    # 2. 파일 열기
    with file_path.open(encoding='utf-8') as f:
        books = json.load(f)  # 파일을 열고 JSON 데이터를 읽은 뒤 Python dictionary로 변환

    # 3. 출판일 기준으로 도서를 월별로 분류
    monthly_prices = {month: 0 for month in range(1, 13)}  # 월별 가격 합계
    monthly_counts = {month: 0 for month in range(1, 13)}  # 월별 도서 수

    for book in books:
        pub_date = datetime.strptime(book['pubDate'], '%Y-%m-%d')
        month = pub_date.month

        monthly_prices[month] += book['priceSales']
        monthly_counts[month] += 1

    # 4. 월별 도서 가격을 합산하고, 도서 수를 구하여 각 월의 평균 가격을 계산
    print("월별 평균 가격 및 도서 수:")
    for month in range(1, 13):
        count = monthly_counts[month]
        if count > 0:
            average_price = monthly_prices[month] / count
        else:
            average_price = 0

        print(f"{month}월: 평균 가격 {average_price:.2f}원 (총 {count}권)")
else:
    print(f"파일이 존재하지 않습니다: {file_path}")
