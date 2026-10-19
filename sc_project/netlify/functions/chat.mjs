// OpenAI 호출을 서버에서 처리해 API 키가 브라우저에 노출되지 않도록 한다.
// 클라이언트는 질문만 보내고, 부산 데이터 컨텍스트와 프롬프트는 여기서 구성한다.
import stay from "../../public/data/부산_숙박.json";
import festival from "../../public/data/부산_축제공연행사.json";
import tour from "../../public/data/부산_관광지.json";
import leisure from "../../public/data/부산_레포츠.json";
import culture from "../../public/data/부산_문화시설.json";
import shopping from "../../public/data/부산_쇼핑.json";
import course from "../../public/data/부산_여행코스.json";

const DATA = { stay, festival, tour, leisure, culture, shopping, course };
const MAX_QUESTION_LENGTH = 500;

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

function buildSystemPrompt(question) {
  const context = detectCategories(question)
    .map((key) => `[${CATEGORY_LABELS[key]}]\n${JSON.stringify(DATA[key]).slice(0, 8000)}`)
    .join("\n\n");

  return `
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
`;
}

const json = (body, status = 200) => Response.json(body, { status });

export default async (req) => {
  if (req.method !== "POST") {
    return json({ error: "POST 요청만 지원합니다." }, 405);
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return json({ error: "서버에 OPENAI_API_KEY가 설정되지 않았습니다." }, 500);
  }

  let question;
  try {
    ({ question } = await req.json());
  } catch {
    return json({ error: "요청 형식이 올바르지 않습니다." }, 400);
  }
  if (typeof question !== "string" || !question.trim()) {
    return json({ error: "질문을 입력해주세요." }, 400);
  }
  if (question.length > MAX_QUESTION_LENGTH) {
    return json({ error: `질문은 ${MAX_QUESTION_LENGTH}자 이내로 입력해주세요.` }, 400);
  }

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL || "gpt-5-mini",
      messages: [
        { role: "system", content: buildSystemPrompt(question) },
        { role: "user", content: question }
      ]
    })
  });

  const result = await response.json();
  if (!response.ok) {
    console.error("OpenAI 요청 실패:", response.status, result.error?.message);
    return json({ error: "답변을 가져오지 못했습니다. 잠시 후 다시 시도해주세요." }, 502);
  }

  return json({ answer: result.choices[0].message.content });
};

export const config = { path: "/api/chat" };
