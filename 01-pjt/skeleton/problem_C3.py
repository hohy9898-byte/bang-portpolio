from pathlib import Path
import json

# 시리즈 정보가 있는 책들 끼리 묶기
# 아래에 생성형 AI를 활용한 코드 작성

# 1. 디렉토리 경로 설정 (data/series_items 사용)
series_dir = Path('./skeleton/data/series_items')  # 시리즈 폴더가 모여있는 디렉토리

# 디렉토리 존재 여부 확인
if series_dir.exists():  # 디렉토리가 존재할 경우
    series_data = {}  # 시리즈별 정보를 저장할 딕셔너리

    # 2. 디렉토리 내의 모든 폴더 순회
    for series_folder in series_dir.iterdir():
        if not series_folder.is_dir():
            continue

        series_id = series_folder.name  # 폴더 이름이 곧 seriesId
        books = []
        series_name = ''

        # 3. 폴더 내의 모든 JSON 파일 순회
        for json_file in series_folder.glob('*.json'):
            with json_file.open(encoding='utf-8') as f:
                book = json.load(f)  # 책 정보를 담은 JSON 파일 읽기

            books.append(book)

            # 시리즈 이름은 seriesInfo가 있는 파일에서 추출
            if not series_name and 'seriesInfo' in book:
                series_name = book['seriesInfo']['seriesName']

        # 4. 시리즈 정보와 해당 시리즈에 속한 책 정보를 리스트로 저장
        series_data[series_id] = {
            'seriesId': int(series_id),
            'seriesName': series_name,
            'books': books,
        }

    # 5. 병합된 시리즈 정보를 담은 새로운 JSON 파일 생성
    output_path = Path('./skeleton/data/series.json')
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(series_data, f, ensure_ascii=False, indent=2)

    print("모든 시리즈 데이터가 series.json 파일로 병합되었습니다.")
else:
    print(f"디렉토리가 존재하지 않습니다: {series_dir}")
