"""
알라딘 OpenAPI 로 도서 100권의 책 소개, 표지 URL 을 받아 book_details.json 에 저장

    1. https://www.aladin.co.kr/ttb/wblog_manage.aspx 에서 TTB 키 발급
    2. .env 에 ALADIN_TTB_KEY="발급받은 키" 추가
    3. python fetch_book_details.py
    4. python set_vector_store.py  (책 소개를 포함해 벡터 DB 다시 생성)

이미 받은 도서는 건너뛰므로 중간에 실패해도 다시 실행하면 이어서 받는다.
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request

from dotenv import load_dotenv

from books import DETAILS_FILE, load_books, load_details, normalize

load_dotenv()

API_URL = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"


def lookup(ttb_key: str, isbn: str) -> dict | None:
    params = urllib.parse.urlencode(
        {
            "ttbkey": ttb_key,
            "itemIdType": "ISBN13",
            "ItemId": isbn,
            "output": "js",
            "Version": "20131101",
            "Cover": "Big",
        }
    )
    with urllib.request.urlopen(f"{API_URL}?{params}", timeout=10) as res:
        data = json.loads(res.read().decode("utf-8"))
    if data.get("errorCode"):
        raise RuntimeError(f"{data.get('errorCode')}: {data.get('errorMessage')}")
    items = data.get("item") or []
    if not items:
        return None
    item = items[0]
    return {
        "aladin_title": item.get("title", ""),
        "description": item.get("description", "").strip(),
        "cover": item.get("cover", ""),
    }


def same_book(title: str, aladin_title: str) -> bool:
    """샘플 데이터의 ISBN 이 다른 책을 가리킬 수 있으므로 제목이 맞는지 확인"""
    a = normalize(re.sub(r"\s*\(.*?\)", "", title))
    b = normalize(aladin_title)
    return a in b or b in a


def main() -> None:
    ttb_key = os.getenv("ALADIN_TTB_KEY")
    if not ttb_key:
        raise SystemExit(".env 에 ALADIN_TTB_KEY 를 설정하세요.")

    details = load_details()
    not_found, mismatched = [], []
    for book in load_books():
        isbn = book["isbn"]
        if isbn in details:
            continue
        try:
            detail = lookup(ttb_key, isbn)
        except Exception as e:
            print(f"[오류] {book['title']} ({isbn}): {e}")
            continue
        if detail is None:
            not_found.append(book["title"])
            print(f"[없음] {book['title']} ({isbn})")
            continue
        if not same_book(book["title"], detail["aladin_title"]):
            mismatched.append(f"{book['title']} -> {detail['aladin_title']}")
            print(f"[불일치] {book['title']} ({isbn}) -> {detail['aladin_title']}")
            continue
        details[isbn] = detail
        print(f"[완료] {book['title']} -> {detail['aladin_title']}")
        # 받을 때마다 저장해 두어 중간에 멈춰도 이어서 받을 수 있게 함
        with open(DETAILS_FILE, "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        time.sleep(0.2)

    print(f"\n저장: {DETAILS_FILE} ({len(details)}권)")
    if not_found:
        print(f"ISBN 으로 찾지 못한 도서 {len(not_found)}권: {not_found}")
    if mismatched:
        print(f"ISBN 이 다른 책을 가리켜 저장하지 않은 도서 {len(mismatched)}권:")
        for m in mismatched:
            print(f"  - {m}")


if __name__ == "__main__":
    main()
