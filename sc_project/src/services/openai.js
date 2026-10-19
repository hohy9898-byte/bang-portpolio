import { loadData } from "./data";

const API_KEY = import.meta.env.VITE_OPENAI_API_KEY;
const MODEL = import.meta.env.VITE_OPENAI_MODEL;

// 질문 키워드로 관련 카테고리만 골라내어 컨텍스트 크기를 줄이기 위한 매핑
const CATEGORY_KEYWORDS = {
  stay: ["숙박", "호텔", "모텔", "펜션", "게스트하우스", "숙소", "묵을", "잠잘"],
  festival: ["축제", "행사", "공연", "페스티벌", "이벤트"],
  tour: ["관광지", "관광", "명소", "여행지", "볼거리", "가볼만한", "가볼 만한"],
  leisure: ["레포츠", "액티비티", "체험", "서핑", "스쿠버", "하이킹", "등산", "캠핑"],
  culture: ["문화시설", "박물관", "미술관", "전시관", "전시", "도서관", "공연장"],
  shopping: ["쇼핑", "시장", "백화점", "아울렛", "상점", "마켓"],
  course: ["여행코스", "코스", "일정", "루트", "당일치기", "데이트코스"]
};

const CATEGORY_LABELS = {
  stay: "부산 숙박 데이터",
  festival: "부산 축제 데이터",
  tour: "부산 관광지 데이터",
  leisure: "부산 레포츠 데이터",
  culture: "부산 문화시설 데이터",
  shopping: "부산 쇼핑 데이터",
  course: "부산 여행코스 데이터"
};

// 질문에 해당하는 카테고리만 선별 (매칭이 없으면 전체를 사용해 안전하게 폴백)
function detectCategories(question) {
  const matched = Object.keys(CATEGORY_KEYWORDS).filter((key) =>
    CATEGORY_KEYWORDS[key].some((keyword) => question.includes(keyword))
  );
  return matched.length > 0 ? matched : Object.keys(CATEGORY_KEYWORDS);
}

export async function askGPT(question) {

  // JSON 데이터 불러오기
  const data = await loadData();

  // 질문과 관련된 카테고리 데이터만 컨텍스트로 구성 (프롬프트 크기 축소 → 응답 속도 개선)
  const categories = detectCategories(question);
  const context = categories
    .map((key) => `[${CATEGORY_LABELS[key]}]\n${JSON.stringify(data[key]).slice(0, 8000)}`)
    .join("\n\n");

  const response = await fetch(
    "https://api.openai.com/v1/chat/completions",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          {
            role: "system",
            content: `
당신은 부산 관광 전문 챗봇입니다.

반드시 아래 JSON 데이터를 우선 참고하여 답변하세요.

규칙
1. 데이터에 있는 내용이면 데이터를 기반으로 답변한다.
2. 데이터에 없으면 일반 관광 지식으로 답변한다.
3. 숙박 질문은 숙박 데이터를 참고한다.
4. 축제 질문은 축제 데이터를 참고한다.
5. 관광지 질문은 관광지 데이터를 참고한다.
6. 문화시설 질문은 문화시설 데이터를 참고한다.
7. 쇼핑 질문은 쇼핑 데이터를 참고한다.
8. 레포츠 질문은 레포츠 데이터를 참고한다.
9. 여행코스 질문은 여행코스 데이터를 참고한다.

데이터:
${context}
`
          },
          {
            role: "user",
            content: question
          }
        ]
      })
    }
  );

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.error?.message || `OpenAI 요청 실패 (status ${response.status})`);
  }

  return result.choices[0].message.content;
}