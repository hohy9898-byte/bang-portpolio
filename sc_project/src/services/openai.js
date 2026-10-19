// OpenAI 호출은 Netlify Function(netlify/functions/chat.mjs)에서 처리한다.
// API 키가 빌드 결과물에 포함되지 않도록 클라이언트는 질문만 전달한다.
export async function askGPT(question) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  const result = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(result.error || `챗봇 요청 실패 (status ${response.status})`);
  }

  return result.answer;
}
