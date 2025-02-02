import pdfplumber
import re
import pandas as pd

# PDF 파일 경로
pdf_path = "250203.pdf"

def extract_protest_schedule(pdf_path):
    schedules = []

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # 정규표현식 패턴 (멀티라인 지원: 장소 → 시간/인원/관할서 → 지역)
    pattern = re.compile(r"(.+?)\n(\d{1,2}:\d{2}~\d{1,2}:\d{2})\s+([\d,]+)\s+(.+?)\n<(.+?)>", re.MULTILINE)

    for match in pattern.findall(text):
        location, time_range, expected_people, police_department, region = match
        schedules.append({
            "시간": time_range,
            "장소": location.strip(),
            "예상 인원": int(expected_people.replace(",", "")),  # 숫자 콤마 제거
            "관할서": police_department.strip(),
            "지역": region.strip()
        })

    return schedules

# ✅ 시위 일정 추출
protest_list = extract_protest_schedule(pdf_path)

# ✅ DataFrame 변환 후 CSV 저장
df = pd.DataFrame(protest_list)
csv_file_path = "protest_schedule.csv"
df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")

print(f"✅ CSV 파일 저장 완료: {csv_file_path}")
