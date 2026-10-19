"""
도서 검색: 벡터 검색 + 키워드(BM25) 검색을 RRF 로 합친 하이브리드 검색
- 벡터 검색: 주제, 분위기처럼 단어가 정확히 일치하지 않는 질문에 강함
- 키워드 검색: 제목, 저자, 고유명사("파이썬", "토익")처럼 단어가 그대로 나오는 질문에 강함
"""

import math
from collections import Counter

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from books import normalize

# Qwen3-Embedding 은 검색어(query)에 작업 지시문을 붙이면 검색 정확도가 올라가도록 학습됨
# (저장하는 문서 쪽에는 붙이지 않음)
QUERY_INSTRUCTION = "Given a user's request about books, retrieve books in the catalog that match the request"


class QwenEmbeddings(OllamaEmbeddings):
    def embed_query(self, text: str) -> list[float]:
        return super().embed_query(f"Instruct: {QUERY_INSTRUCTION}\nQuery: {text}")


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="books",
        embedding_function=QwenEmbeddings(model="qwen3-embedding:4b"),
        persist_directory="./chroma_store",
    )


def bigrams(text: str) -> list[str]:
    """한국어는 띄어쓰기/조사 때문에 단어 단위가 불안정하므로 글자 2개씩 잘라 비교"""
    text = normalize(text)
    if len(text) < 2:
        return [text] if text else []
    return [text[i : i + 2] for i in range(len(text) - 1)]


class BM25:
    def __init__(self, books: list[dict], k1: float = 1.5, b: float = 0.75):
        self.books = books
        self.k1, self.b = k1, b
        self.docs = [
            Counter(bigrams(f"{bk['title']} {bk['author']} {bk['publisher']} {bk['category']} {bk['description']}"))
            for bk in books
        ]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg_len = sum(self.lengths) / len(self.lengths)
        df = Counter(term for d in self.docs for term in d)
        n = len(books)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query: str, k: int) -> list[dict]:
        terms = set(bigrams(query))
        scores = []
        for book, doc, length in zip(self.books, self.docs, self.lengths):
            score = 0.0
            for t in terms:
                tf = doc.get(t, 0)
                if tf:
                    norm = tf + self.k1 * (1 - self.b + self.b * length / self.avg_len)
                    score += self.idf[t] * tf * (self.k1 + 1) / norm
            if score > 0:
                scores.append((score, book))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [book for _, book in scores[:k]]


class HybridRetriever:
    def __init__(self, books: list[dict], vector_store: Chroma):
        self.by_isbn = {b["isbn"]: b for b in books}
        self.vector_store = vector_store
        self.bm25 = BM25(books)

    def search(self, query: str, k: int = 5, candidates: int = 20, rrf_k: int = 60) -> list[dict]:
        vector_hits = [
            self.by_isbn[doc.metadata["isbn"]]
            for doc in self.vector_store.similarity_search(query, k=candidates)
            if doc.metadata.get("isbn") in self.by_isbn
        ]
        keyword_hits = self.bm25.search(query, k=candidates)

        # RRF(Reciprocal Rank Fusion): 점수 스케일이 다른 두 결과를 순위만으로 합침
        scores = Counter()
        for hits in (vector_hits, keyword_hits):
            for rank, book in enumerate(hits):
                scores[book["isbn"]] += 1 / (rrf_k + rank + 1)
        return [self.by_isbn[isbn] for isbn, _ in scores.most_common(k)]
