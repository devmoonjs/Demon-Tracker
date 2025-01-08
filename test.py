import re
from PyPDF2 import PdfReader

# PDF 파일 경로
pdf_file_path = "테스트파일.pdf"

# PDF 텍스트 추출
reader = PdfReader(pdf_file_path)
pdf_text = ""

for page in reader.pages:
    pdf_text += page.extract_text()
    # print(pdf_text)

# 정규식으로 필요한 정보 추출
# 정규식 패턴
pattern = r"(\d{1,2}:\d{2}~[^\n]+?)<([^>]+)>\s*([\d,]+)\s*(\S+)\s+(\S+)"

# 데이터 추출
matches = re.findall(pattern, pdf_text)

# 결과 정리
protests = []
for match in matches:
    time, location, attendees, police, note = match
    protests.append({
        "일시": time.strip(),
        "장소": location.strip(),
        "인원": attendees.replace(",", "").strip(),
        "관할서": police.strip(),
        "비고": note.strip(),
    })

# 결과 출력
for idx, protest in enumerate(protests, start=1):
    print(f"{idx}. 일시: {protest['일시']}, 장소: {protest['장소']}, 인원: {protest['인원']}명, 관할서: {protest['관할서']}, 비고: {protest['비고']}")