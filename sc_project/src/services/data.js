let cachedDataPromise = null;

async function fetchJson(path) {
  const res = await fetch(path);
  return res.json();
}

export function loadData() {
  if (!cachedDataPromise) {
    cachedDataPromise = Promise.all([
      fetchJson("/data/부산_숙박.json"),
      fetchJson("/data/부산_축제공연행사.json"),
      fetchJson("/data/부산_관광지.json"),
      fetchJson("/data/부산_레포츠.json"),
      fetchJson("/data/부산_문화시설.json"),
      fetchJson("/data/부산_쇼핑.json"),
      fetchJson("/data/부산_여행코스.json")
    ]).then(([stay, festival, tour, leisure, culture, shopping, course]) => ({
      stay,
      festival,
      tour,
      leisure,
      culture,
      shopping,
      course
    }));
  }

  return cachedDataPromise;
}
