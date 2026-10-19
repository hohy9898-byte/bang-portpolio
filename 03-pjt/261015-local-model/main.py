import os
import re
from difflib import SequenceMatcher
from typing import Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

from books import CATEGORIES, build_aliases, find_bold_titles, find_books, format_book, load_books, normalize
from retriever import HybridRetriever, get_vector_store

load_dotenv()

BOOKS = load_books()
TITLE_ALIASES = build_aliases(BOOKS)

retriever = HybridRetriever(BOOKS, get_vector_store())


@tool(response_format="content_and_artifact")
def search_books_info(query: str) -> tuple[str, list[dict]]:
    """
    도서의 내용, 주제, 분위기, 제목, 작가 등으로 비슷한 도서를 검색합니다.
    출간연도, 가격, 분류, 순위 같은 정확한 조건이 있으면 filter_books 를 사용하세요.

    Args:
        query (str): 검색할 핵심 질의. 예) "우주 SF 소설", "투자 입문서", "한강"
    """
    books = retriever.search(query, k=5)
    return "\n".join(format_book(book) for book in books), books


def author_matches(query: str, author: str) -> bool:
    """띄어쓰기 차이나 모델의 오타("헤르ман 헤세")가 있어도 저자를 찾도록 비슷한 이름까지 허용"""
    q, a = normalize(query), normalize(author)
    if not q:
        return False
    return q in a or SequenceMatcher(None, q, a).ratio() >= 0.75


@tool
def filter_books(
    category: Optional[str] = None,
    author: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort_by: str = "rank",
    limit: int = 30,
) -> str:
    """
    조건에 맞는 도서를 정확하게 찾습니다. 모든 조건은 선택 사항입니다.

    Args:
        category: 분류. 다음 중 하나 - 소설/시/희곡, 경제경영, 인문, 자기계발, 자연과학, 역사, 어린이, 외국어, 수험서/자격증, 건강/취미
        author: 저자 이름 (일부만 입력해도 됨)
        year_from: 이 연도 이후(포함) 출간
        year_to: 이 연도 이전(포함) 출간
        min_price: 가격 하한(원, 이 값 포함). 금액과 함께 "넘는", "초과", "이상", "부터" 라고 할 때만 사용. "넘는/초과"는 1을 더해서 입력
        max_price: 가격 상한(원, 이 값 포함). 금액과 함께 "이하", "미만", "까지" 라고 할 때만 사용. "미만"은 1을 빼서 입력
        sort_by: 정렬 기준. rank(베스트셀러 순위), price(가격 낮은 순), price_desc(가격 높은 순), newest(최신순).
            "가장 비싼/싼", "최신" 처럼 금액 없이 순서를 묻는 질문은 가격 조건 없이 sort_by 와 limit 만 사용
        limit: 최대 결과 수. 사용자가 "3권"처럼 개수를 말한 경우에만 지정
    """
    # 모델이 조건 없음을 0 으로 넣는 경우가 있어 0 이하는 조건 없음으로 처리
    min_price = min_price if min_price and min_price > 0 else None
    max_price = max_price if max_price and max_price > 0 else None

    results = [
        book
        for book in BOOKS
        if (category is None or book["category"] == category)
        and (author is None or author_matches(author, book["author"]))
        and (year_from is None or book["year"] >= year_from)
        and (year_to is None or book["year"] <= year_to)
        and (min_price is None or book["price"] >= min_price)
        and (max_price is None or book["price"] <= max_price)
    ]

    sort_keys = {
        "rank": (lambda b: b["rank"], False),
        "price": (lambda b: b["price"], False),
        "price_desc": (lambda b: b["price"], True),
        "newest": (lambda b: b["pub_date"], True),
    }
    key, reverse = sort_keys.get(sort_by, sort_keys["rank"])
    results.sort(key=key, reverse=reverse)

    if not results:
        return "조건에 맞는 도서가 없습니다."
    lines = [format_book(book) for book in results[:limit]]
    return f"총 {len(results)}권 중 {len(lines)}권:\n" + "\n".join(lines)


SYSTEM_PROMPT = f"""
너는 도서 플랫폼 ThRead 의 도서 추천 챗봇이다.
항상 한국어로 간결하게 답변한다.
보유 도서는 베스트셀러 100권이며, 분류는 {", ".join(CATEGORIES)} 이다.

다음 툴을 사용할 수 있다.
  - filter_books : 분류, 저자, 출간연도, 가격, 순위 등 정확한 조건으로 도서를 찾을 때 사용
  - search_books_info : 주제, 내용, 분위기 등으로 비슷한 도서를 찾을 때 사용

규칙
1. 도서, 작가, 추천, 보유 여부에 관한 질문은 기억으로 답하지 말고 반드시 먼저 툴을 호출한다.
   보유 도서에 없다고 답하는 것도 툴 결과를 확인한 뒤에만 한다.
   - 저자 이름이 나오면 filter_books(author=...)
   - 분류, 연도, 가격, 순위 조건이 있으면 filter_books (사용자가 말하지 않은 조건은 넣지 않는다)
   - 주제나 키워드("파이썬", "요리", "SF", "인류의 역사")는 search_books_info
     분류 이름과 정확히 같은 말이 아니면 분류로 거르지 말고 search_books_info 를 사용한다
2. 도서에 관한 답변은 반드시 툴 결과에 있는 도서만 사용하고, 툴 결과에 없는 도서나 정보는 지어내지 않는다.
3. 툴 결과의 조건을 다시 판단하지 말고, 결과에 나온 도서를 하나도 빠뜨리지 말고 그대로 정리해서 보여준다.
4. 특정 도서와 비슷한 책을 추천할 때는 그 도서와 같은 분류를 filter_books 로 찾고, 그 도서 자체는 추천에서 제외한다.
5. 인사, 챗봇 소개 같은 일반적인 대화는 툴을 사용하지 않고 답변한다.
"""

llm = ChatOpenAI(
    base_url=os.getenv("BASE_URL"),
    model="qwen3:4b-instruct-2507-q4_K_M",
    api_key="no_need",
)

# 에이전트 생성 (checkpointer: session_id 별로 대화 기록 유지)
agent = create_agent(
    model=llm,
    tools=[filter_books, search_books_info],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    # 도서 상세 페이지에서 보고 있는 도서 제목
    book_title: Optional[str] = None


class BookCard(BaseModel):
    title: str
    author: str
    publisher: str
    category: str
    price: int
    pub_date: str
    isbn: str
    cover: str = ""


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    # 답변에 등장한 보유 도서 (프론트엔드의 도서 카드용)
    books: list[BookCard] = []


AUTHORS = {normalize(b["author"]) for b in BOOKS}
# 모델이 표 머리글이나 항목 이름으로 굵게 쓰는 단어
FIELD_WORDS = {normalize(w) for w in ["책 제목", "제목", "저자", "출판사", "분류", "가격", "출간일", "출간 연도", "순위", "소개"]}
FIELD_WORDS |= {normalize(c) for c in CATEGORIES}


def find_unverified_titles(answer: str) -> list[str]:
    """**굵게** 표시됐지만 보유 도서 제목도, 저자도 아닌 부분 (모델이 지어낸 도서일 가능성)"""
    unverified = []
    for text in find_bold_titles(answer):
        key = normalize(text)
        if not key or key in AUTHORS or key in FIELD_WORDS or find_books(text, TITLE_ALIASES):
            continue
        # "12,000원", "2022년", "3권" 같은 숫자 값
        if re.fullmatch(r"[\d,.\s]+(원|년|권|위)?", text.strip(" :")):
            continue
        unverified.append(text)
    return unverified


def ask(prompt: str, session_id: str, book_title: Optional[str] = None) -> list:
    """에이전트에 질문하고, 이번 턴에 추가된 메시지(툴 호출 포함) 리스트를 반환"""
    if book_title:
        current = next((b for b in BOOKS if b["title"] == book_title), None)
        book_info = format_book(current) if current else book_title
        prompt = f"(사용자가 현재 보고 있는 도서: {book_info})\n{prompt}"

    config = {"configurable": {"thread_id": session_id}}
    before = len(agent.get_state(config).values.get("messages", []))
    response = agent.invoke({"messages": [("user", prompt)]}, config=config)
    return response["messages"][before:]


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest) -> ChatResponse:
    session_id = chat_request.session_id or str(uuid4())
    messages = ask(chat_request.prompt, session_id, chat_request.book_title)
    answer = messages[-1].content

    unverified = find_unverified_titles(answer)
    if unverified:
        print(f"[경고] 보유 도서에서 찾을 수 없는 제목: {unverified}")

    # 상세 화면에서 보고 있는 도서는 카드에서 제외
    books = [b for b in find_books(answer, TITLE_ALIASES) if b["title"] != chat_request.book_title]
    return {"answer": answer, "session_id": session_id, "books": books}
