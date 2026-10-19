import json  # 파이썬 객체 <-> JSON 문자열 변환을 위한 라이브러리
import random  # 가상 데이터를 무작위로 뽑아내기 위한 라이브러리
import shutil  # 기존 파일을 백업(복사)하기 위한 라이브러리
from datetime import date, datetime, timedelta  # 출간일(pubDate)/백업 시각을 가상으로 생성하기 위한 라이브러리
from pathlib import Path  # OS에 상관없이 안전하게 파일 경로를 다루기 위한 라이브러리

# 매번 실행해도 같은 가상 데이터가 나오도록 랜덤 시드를 고정
# (시드를 고정하지 않으면 실행할 때마다 다른 책이 만들어져서 결과 비교가 어려움)
random.seed(42)

# 1. 가상 데이터를 만들 때 재료로 사용할 후보 목록들
#    실제 알라딘 API 응답(books_500.json 등)의 필드 구성을 그대로 흉내내기 위해
#    title/author/publisher/categoryName 등 같은 키 이름을 사용한다.
titles = [
    "은하수를 건너는 고양이", "밤의 도서관", "12번째 행성의 비밀",
    "말하는 나무의 노래", "시간을 파는 상점 2", "구름 공장 이야기",
    "붉은 등대지기", "잊혀진 마을의 지도", "별빛 수선공",
    "안개 마을 탐정단", "종이배를 타고", "숲속 우체국",
    "달팽이의 여행법", "겨울잠을 자는 로봇", "빛나는 조약돌",
    "마지막 책방지기", "고요한 강가에서", "하늘을 나는 자전거",
    "작은 씨앗의 꿈", "유리병 속 편지",
]

authors = [
    "김하늘 (지은이)", "이도윤 (지은이), 박서연 (그림)", "최은서 (지은이)",
    "정민준 (지은이), 한지우 (옮긴이)", "오세아 (지은이)", "강태오 (지은이), 문가을 (그림)",
]

publishers = ["초록달 출판사", "은하수 미디어", "파랑새 북스", "구름다리 출판", "햇살출판사"]

category_names = [
    "국내도서>소설/시/희곡>한국소설>2020년대 한국소설",
    "국내도서>어린이>동화/명작/고전>국내창작동화",
    "국내도서>유아>그림책>나라별 그림책>한국 그림책",
    "국내도서>과학>과학교양",
    "국내도서>에세이>한국에세이",
]


def make_fake_isbn13(index: int) -> str:
    """13자리 숫자로 구성된 가상의 isbn13 값을 만드는 함수 (실제 출판사 대역과 충돌하지 않도록 979-11 접두를 사용)"""
    # index를 이용해 뒷자리를 채워 20권이 서로 겹치지 않는 고유 번호가 되도록 함
    return f"979114{index:06d}"


def make_fake_pub_date() -> str:
    """오늘로부터 최근 3년(1095일) 이내의 임의의 날짜를 'YYYY-MM-DD' 문자열로 생성"""
    days_ago = random.randint(0, 1095)
    pub_date = date.today() - timedelta(days=days_ago)
    return pub_date.isoformat()


# 2. 20권의 가상 도서 정보를 담을 리스트
virtual_books = []

for i in range(20):
    # 2-1. 정가(priceStandard)를 8,000 ~ 25,000원 사이에서 500원 단위로 무작위 결정
    price_standard = random.randrange(8000, 25000, 500)

    # 2-2. 할인율을 0% ~ 20% 사이에서 무작위로 정하고, 판매가(priceSales)를 계산
    discount_rate = random.choice([0, 5, 10, 10, 15, 20])
    price_sales = int(price_standard * (100 - discount_rate) / 100)

    # 2-3. 마일리지는 판매가의 5%로 계산 (알라딘 실제 정책과 유사하게 흉내)
    mileage = int(price_sales * 0.05)

    # 2-4. 한 권의 가상 도서 정보를 딕셔너리로 구성
    #      (기존 books_20.json/books_500.json과 동일한 key 이름을 사용해
    #       problem_A1~A5.py 등 기존 코드를 수정 없이 그대로 실습할 수 있게 함)
    book = {
        "title": titles[i],
        "link": f"http://example.com/shop/wproduct.aspx?ItemId=90000{i:03d}",
        "author": random.choice(authors),
        "pubDate": make_fake_pub_date(),
        "description": f"{titles[i]}에 대한 가상의 도서 소개 문구입니다.",
        "isbn": f"V{900000000 + i}",
        "isbn13": make_fake_isbn13(i),
        "itemId": 900000000 + i,
        "priceSales": price_sales,
        "priceStandard": price_standard,
        "mallType": "BOOK",
        "stockStatus": "",
        "mileage": mileage,
        "cover": f"https://example.com/cover/{900000000 + i}.jpg",
        "categoryId": 10000 + i,
        "categoryName": random.choice(category_names),
        "publisher": random.choice(publishers),
        "salesPoint": random.randint(0, 5000),
        "adult": False,
        "fixedPrice": True,
        "customerReviewRank": random.choice([0, 6, 7, 8, 9, 10]),
        "subInfo": {},
    }
    virtual_books.append(book)

# 3. 알라딘 검색 API 응답 형식과 동일하게 상위 메타데이터 + item 리스트로 감싸기
#    (problem_A1~A5.py 가 data['item']으로 접근하므로 이 구조를 유지해야 함)
result = {
    "version": "20131101",
    "title": "가상 도서 검색결과 - 테스트용",
    "pubDate": date.today().isoformat(),
    "totalResults": len(virtual_books),
    "startIndex": 1,
    "itemsPerPage": len(virtual_books),
    "query": "가상 도서",
    "searchCategoryId": 0,
    "searchCategoryName": "전체",
    "item": virtual_books,
}

# 4. 저장할 파일 경로 설정
#    Path(__file__).parent: 이 스크립트가 있는 skeleton 폴더를 기준으로 경로를 잡아
#    어느 위치에서 실행하더라도 항상 skeleton/data/books_20.json 을 가리키게 함
output_path = Path(__file__).parent / "data" / "books_20.json"

# 5. 폴더가 없을 경우를 대비해 생성 (이미 있으면 아무 동작도 하지 않음)
output_path.parent.mkdir(parents=True, exist_ok=True)

# 6. 같은 이름의 파일이 이미 있으면 덮어쓰기 전에 타임스탬프를 붙여 백업
#    (예: books_20.json -> books_20.20260729_153000.bak.json)
if output_path.exists():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = output_path.with_name(
        f"{output_path.stem}.{timestamp}.bak{output_path.suffix}"
    )
    shutil.copy2(output_path, backup_path)
    print(f"기존 파일을 백업했습니다: {backup_path}")

# 7. JSON 파일로 저장 (새 가상 데이터로 덮어쓰기)
#    ensure_ascii=False: 한글이 유니코드 이스케이프(\uXXXX)가 아닌 문자 그대로 저장되도록 함
#    indent=4: 사람이 읽기 좋게 들여쓰기 포함해서 저장
with output_path.open("w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

# 8. 완료 메시지 출력
print(f"가상 도서 {len(virtual_books)}권을 생성하여 저장했습니다: {output_path}")
