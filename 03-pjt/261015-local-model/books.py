import json
import os
import re

from langchain_core.documents import Document

BOOKS_FILE = "./books.txt"
# fetch_book_details.py 로 받은 책 소개, 표지 URL (없으면 기본 필드만 사용)
DETAILS_FILE = "./book_details.json"

CATEGORIES = [
    "소설/시/희곡",
    "경제경영",
    "인문",
    "자기계발",
    "자연과학",
    "역사",
    "어린이",
    "외국어",
    "수험서/자격증",
    "건강/취미",
]


def load_details(file_path: str = DETAILS_FILE) -> dict:
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_books(file_path: str = BOOKS_FILE) -> list[dict]:
    """books.txt 에서 도서 데이터 줄(Rank|Title|...)만 읽어 dict 리스트로 반환"""
    details = load_details()
    books = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            fields = line.strip().split("|")
            if len(fields) != 8 or not fields[0].isdigit():
                continue
            rank, title, author, publisher, category, price, pub_date, isbn = fields
            detail = details.get(isbn, {})
            books.append(
                {
                    "rank": int(rank),
                    "title": title,
                    "author": author,
                    "publisher": publisher,
                    "category": category,
                    "price": int(price),
                    "pub_date": pub_date,
                    "year": int(pub_date[:4]),
                    "isbn": isbn,
                    # Chroma metadata 는 None 을 저장할 수 없어 빈 문자열 사용
                    "description": detail.get("description", ""),
                    "cover": detail.get("cover", ""),
                }
            )
    return books


def format_book(book: dict) -> str:
    """툴 결과로 모델에게 전달하는 한 줄 요약"""
    text = (
        f"[베스트셀러 {book['rank']}위] {book['title']} | 저자: {book['author']} | "
        f"출판사: {book['publisher']} | 분류: {book['category']} | "
        f"가격: {book['price']:,}원 | 출간일: {book['pub_date']}"
    )
    if book.get("description"):
        text += f" | 소개: {book['description'][:150]}"
    return text


def to_document(book: dict) -> Document:
    """도서 1권 = Document 1개. 임베딩에는 책 소개 전체를 포함"""
    content = format_book(book)
    if book.get("description"):
        content = content.split(" | 소개: ")[0] + f"\n소개: {book['description']}"
    return Document(page_content=content, metadata=book)


# ===== 답변에서 도서 제목 찾기 (응답의 도서 카드, 평가 스크립트에서 사용) =====
def normalize(text: str) -> str:
    """공백, 문장부호를 지우고 소문자로 (모델이 띄어쓰기나 괄호를 다르게 써도 매칭되도록)"""
    return re.sub(r"[^0-9a-z가-힣]", "", text.lower())


def build_aliases(books: list[dict]) -> list[tuple[str, dict]]:
    """(정규화된 별칭, 도서) 목록. '원씽 (The One Thing)' 은 '원씽' 으로도 찾는다"""
    aliases = []
    for book in books:
        title = book["title"]
        aliases.append((normalize(title), book))
        short = re.sub(r"\s*\(.*?\)", "", title)
        if short != title:
            aliases.append((normalize(short), book))
    # 긴 제목부터 찾고 지워야 짧은 제목이 긴 제목 안에서 잘못 잡히지 않음
    return sorted(aliases, key=lambda a: len(a[0]), reverse=True)


def find_books(answer: str, aliases: list[tuple[str, dict]]) -> list[dict]:
    """답변에 등장한 보유 도서를 등장 순서대로 반환"""
    text = normalize(answer)
    found = {}
    for alias, book in aliases:
        pos = text.find(alias)
        if alias and pos >= 0:
            found.setdefault(book["isbn"], (pos, book))
            text = text.replace(alias, "|" * len(alias))  # 위치가 밀리지 않도록 같은 길이로 가림
    return [book for _, book in sorted(found.values(), key=lambda x: x[0])]


def find_bold_titles(answer: str) -> list[str]:
    """답변에서 **굵게** 표시된 부분 (모델이 도서 제목을 주로 굵게 씀)"""
    return [t.strip() for t in re.findall(r"\*\*(.+?)\*\*", answer)]
