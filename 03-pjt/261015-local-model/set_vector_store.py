from dotenv import load_dotenv

from books import load_books, to_document
from retriever import HybridRetriever, get_vector_store

load_dotenv()

books = load_books()
docs = [to_document(book) for book in books]

vector_store = get_vector_store()

# 이전 실행에서 저장된 데이터를 비우고 다시 적재 (중복 방지)
vector_store.reset_collection()
vector_store.add_documents(docs, ids=[book["isbn"] for book in books])

with_description = sum(1 for book in books if book["description"])
print(f"{len(docs)}권 저장 완료 (책 소개 포함 {with_description}권)")
print("=" * 50)

query = "우주를 배경으로 한 SF 소설"
retriever = HybridRetriever(books, vector_store)

print(f"[질문]: {query}")
print("[검색 결과]:")
for book in retriever.search(query, k=5):
    print(f"- {book['title']} ({book['author']}, {book['category']})")
