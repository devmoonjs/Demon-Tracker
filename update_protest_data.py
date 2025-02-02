import pdfplumber
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ✅ PDF 다운로드 관련 함수
def get_board_no(url):
    """게시판에서 최신 파일 ID 가져오기"""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.select_one('#subContents > div > div.inContent > table > tbody > tr:nth-child(1) > td.subject > a')
        match = re.search(r"goBoardView\(.+,'View','(\d+)'\)", str(title))
        return match.group(1) if match else None
    return None

def get_file_id(new_url):
    """파일 ID와 날짜 가져오기"""
    response = requests.get(new_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    link = soup.select_one('#subContents > div > div.inContent > table > tbody > tr:nth-child(3) > td > a:nth-child(3)')
    print(link)

    today_text = link.get_text(strip=True)
    extracted_day = re.search(r'(\d+)', today_text).group(1) if re.search(r'(\d+)', today_text) else None
    file_id = re.search(r"attachfileDownload\('.+','(\d+)'\)", str(link)).group(1) if link else None

    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%y%m%d")
    return (file_id, extracted_day) if extracted_day == tomorrow_date else (None, None)

def download_file(file_id, file_name):
    """PDF 다운로드"""
    url = f"https://www.smpa.go.kr/common/attachfile/attachfileDownload.do?attachNo={file_id}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, "wb") as f:
            f.write(response.content)
        print(f"✅ 파일 다운로드 완료: {file_name}")
        return file_name
    return None

# ✅ PDF → CSV 변환
def extract_protest_schedule(pdf_path):
    """PDF 파일에서 시위 일정 추출"""
    schedules = []
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    pattern = re.compile(r"(.+?)\n(\d{1,2}:\d{2}~\d{1,2}:\d{1,2})\s+([\d,]+)\s+(.+?)\n<(.+?)>", re.MULTILINE)
    for match in pattern.findall(text):
        location, time_range, expected_people, police_department, region = match
        schedules.append({
            "시간": time_range,
            "장소": location.strip(),
            "예상 인원": int(expected_people.replace(",", "")),
            "관할서": police_department.strip(),
            "지역": region.strip()
        })
    return schedules

# ✅ 실행 함수
def main():
    base_url = "https://www.smpa.go.kr/user/nd54882.do"
    
    board_no = get_board_no(base_url)
    if not board_no:
        print("❌ 게시판 번호 가져오기 실패")
        return

    new_url = f"{base_url}?View&uQ=&pageST=SUBJECT&pageSV=&imsi=imsi&page=1&pageSC=SORT_ORDER&pageSO=DESC&dmlType=&boardNo={board_no}&returnUrl=https://www.smpa.go.kr:443/user/nd54882.do"
    file_id, file_name = get_file_id(new_url)
    
    if not file_id:
        print("❌ PDF 파일 ID 가져오기 실패")
        return

    pdf_file = download_file(file_id, f"./data/{file_name}_protest.pdf")
    
    if pdf_file:
        protest_list = extract_protest_schedule(pdf_file)
        df = pd.DataFrame(protest_list)
        csv_path = f"./data/{file_name}_schedule.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"✅ CSV 파일 저장 완료: {csv_path}")

if __name__ == "__main__":
    main()
