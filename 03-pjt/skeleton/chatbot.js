// AI 도서 추천 챗봇 위젯
// - 우측 하단 버튼 또는 data-bs-target="#chatbotOffcanvas" 링크로 채팅창(Offcanvas)을 연다.
// - <body data-book-title="도서명"> 이 있으면 해당 도서를 문맥으로 함께 전송한다.
//   (값은 전송할 때마다 읽으므로, 한 페이지 안에서 화면이 바뀌어도 반영된다)
(() => {
  const API_URL = "http://127.0.0.1:8000/api/v1/chat";

  const getBookTitle = () => document.body.dataset.bookTitle || null;
  const getSuggestions = (bookTitle) =>
    bookTitle
      ? [`${bookTitle}와 비슷한 책 추천해줘`, "이 작가의 다른 책은?"]
      : ["2022년 이후 출간된 소설은?", "2만원 이하 경제경영 책 추천해줘", "한강 작가 책 알려줘"];

  // 대화 기록은 서버가 session_id 별로 유지 (페이지를 새로 열면 새 대화)
  let sessionId = null;

  document.body.insertAdjacentHTML(
    "beforeend",
    `
    <button type="button" class="chatbot-fab" data-bs-toggle="offcanvas"
      data-bs-target="#chatbotOffcanvas" aria-controls="chatbotOffcanvas" aria-label="AI 도서 추천 챗봇 열기">
      <span aria-hidden="true">💬</span>
    </button>

    <div class="offcanvas offcanvas-end chatbot" tabindex="-1" id="chatbotOffcanvas" aria-labelledby="chatbotLabel">
      <div class="offcanvas-header border-bottom">
        <h5 class="offcanvas-title" id="chatbotLabel">Th<span class="read">Read</span> AI 도서 추천</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body chatbot-messages" aria-live="polite"></div>
      <div class="border-top p-3">
        <div class="chatbot-suggestions d-flex flex-wrap gap-2 mb-2"></div>
        <form class="chatbot-form d-flex gap-2">
          <input type="text" class="form-control" placeholder="궁금한 도서를 물어보세요" aria-label="질문 입력" required />
          <button type="submit" class="btn btn-send px-3">전송</button>
        </form>
      </div>
    </div>
    `
  );

  const messages = document.querySelector(".chatbot-messages");
  const form = document.querySelector(".chatbot-form");
  const input = form.querySelector("input");
  const sendButton = form.querySelector("button");
  const suggestionBox = document.querySelector(".chatbot-suggestions");

  // 답변은 마크다운이므로 marked 로 변환 후 DOMPurify 로 정제 (라이브러리가 없으면 일반 텍스트)
  const renderMarkdown = (text) => {
    if (window.marked && window.DOMPurify) {
      return DOMPurify.sanitize(marked.parse(text));
    }
    const div = document.createElement("div");
    div.textContent = text;
    div.style.whiteSpace = "pre-line";
    return div.outerHTML;
  };

  const addMessage = (role, text) => {
    const msg = document.createElement("div");
    msg.className = `chatbot-msg ${role}`;
    if (role === "bot") {
      msg.innerHTML = renderMarkdown(text);
    } else {
      msg.textContent = text;
    }
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
    return msg;
  };

  // 도서 카드: 서버가 표지 URL(알라딘)을 주지 않으면 assets 의 표지를 사용
  const LOCAL_COVERS = {
    "소년이 온다": "assets/bestsellers/img1.jpeg",
    "채식주의자": "assets/bestsellers/img2.jpeg",
    "급류": "assets/bestsellers/img4.jpeg",
    "인간 실격": "assets/bestsellers/img6.jpeg",
    "모순": "assets/bestsellers/img12.jpeg",
  };
  // 상세 화면이 같은 파일에 있으면(08) 화면 전환, 아니면 07 페이지로 이동
  const DETAIL_LINKS = {
    "채식주의자": document.getElementById("book-detail") ? "#book-detail" : "07-book_detail.html",
  };

  const createBookCard = (book) => {
    const link = DETAIL_LINKS[book.title];
    const card = document.createElement(link ? "a" : "div");
    card.className = "chatbot-book";
    if (link) card.href = link;

    const cover = book.cover || LOCAL_COVERS[book.title];
    if (cover) {
      const img = document.createElement("img");
      img.src = cover;
      img.alt = book.title;
      img.loading = "lazy";
      card.appendChild(img);
    } else {
      const placeholder = document.createElement("div");
      placeholder.className = "chatbot-book-placeholder";
      placeholder.textContent = "📖";
      card.appendChild(placeholder);
    }

    const info = document.createElement("div");
    info.className = "chatbot-book-info";
    const title = document.createElement("strong");
    title.textContent = book.title;
    const meta = document.createElement("span");
    meta.textContent = `${book.author} · ${book.price.toLocaleString()}원`;
    info.append(title, meta);
    card.appendChild(info);
    return card;
  };

  const addBookCards = (books) => {
    if (!books || books.length === 0) return;
    const list = document.createElement("div");
    list.className = "chatbot-books";
    books.forEach((book) => list.appendChild(createBookCard(book)));
    messages.appendChild(list);
  };

  const setLoading = (loading) => {
    input.disabled = loading;
    sendButton.disabled = loading;
    suggestionBox.querySelectorAll("button").forEach((btn) => (btn.disabled = loading));
    sendButton.innerHTML = loading
      ? '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span class="visually-hidden">답변 생성 중</span>'
      : "전송";
  };

  const ask = async (prompt) => {
    addMessage("user", prompt);
    setLoading(true);
    const pending = addMessage("bot", "답변을 생성하고 있어요...");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, session_id: sessionId, book_title: getBookTitle() }),
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      sessionId = data.session_id;
      pending.innerHTML = renderMarkdown(data.answer);
      addBookCards(data.books);
    } catch (error) {
      pending.classList.add("error");
      pending.textContent = "챗봇 서버에 연결할 수 없어요. 서버가 실행 중인지 확인해 주세요.";
      console.error(error);
    } finally {
      setLoading(false);
      messages.scrollTop = messages.scrollHeight;
      input.focus();
    }
  };

  const renderSuggestions = () => {
    suggestionBox.replaceChildren();
    getSuggestions(getBookTitle()).forEach((text) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-sm btn-outline-secondary rounded-pill";
      btn.textContent = text;
      btn.disabled = input.disabled;
      btn.addEventListener("click", () => ask(text));
      suggestionBox.appendChild(btn);
    });
  };
  renderSuggestions();

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const prompt = input.value.trim();
    if (!prompt) return;
    input.value = "";
    ask(prompt);
  });

  const offcanvas = document.getElementById("chatbotOffcanvas");
  offcanvas.addEventListener("show.bs.offcanvas", renderSuggestions);
  offcanvas.addEventListener("shown.bs.offcanvas", () => input.focus());

  const bookTitle = getBookTitle();
  addMessage(
    "bot",
    bookTitle
      ? `안녕하세요! **${bookTitle}**에 대해 궁금한 점이나 비슷한 책을 물어보세요.`
      : "안녕하세요! ThRead 도서 추천 챗봇입니다. 보유 중인 베스트셀러 100권에 대해 물어보세요."
  );
})();
