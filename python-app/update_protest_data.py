import pdfplumber
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ✅ PDF 다운로드 관련 함수
def get_board_no(url):
    """게시판에서 최신 파일 ID 가져오기"""
    find_list_size = 5
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%y%m%d")
        tomorrow_date = (datetime.now()).strftime("%y%m%d")

        # 게시판 리스트 중 상위 3개 중 내일 날짜인 게시글 체크
        for i in range(1, find_list_size + 1):
            title_value = f"#subContents > div > div.inContent > table > tbody > tr:nth-child({i}) > td.subject > a"
            title = soup.select_one(title_value)
            title_text = title.text.strip()
            title_text = re.findall(r'\d+', title_text)
            title_text = title_text[0]
            
            if len(title_text) > 6 and title_text[4] == '0':
                title_text = title_text[0:4] + title_text[5:]


            print("title : ",title_text)
            print(tomorrow_date)
            
            if str(tomorrow_date) in str(title_text):
                match = re.search(r"goBoardView\(.+,'View','(\d+)'\)", str(title))
                return match.group(1)

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

    # tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%y%m%d")
    tomorrow_date = (datetime.now()).strftime("%y%m%d")
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
    print(f"text : {text}")

    # 패턴 1: 일반 구조 (명 포함)
    pattern1 = re.compile(
        r"(.+?)\n"
        r"(\d{1,2}:\d{2}~\d{1,2}:\d{2})\s+"
        r"([\d,]+)명\s+"
        r"(.+?)\n<(.+?)>",
        re.MULTILINE
    )

    # 패턴 2: '명' 없이 줄바꿈 + 지역/관할서가 바뀐 경우
    pattern2 = re.compile(
        r"(.+?)\n"
        r"(\d{1,2}:\d{2}~\d{1,2}:\d{2})\s*"
        r"([\d,]+)\n"
        r"<(.+?)>\s+(.+)",
        re.MULTILINE
    )

    for match in pattern1.findall(text):
        location, time_range, expected_people, police_department, region = match
        schedules.append({
            "시간": time_range,
            "장소": location.strip(),
            "예상 인원": int(expected_people.replace(",", "")),
            "관할서": police_department.strip(),
            "지역": region.strip()
        })

    for match in pattern2.findall(text):
        location, time_range, expected_people, region, police_department = match
        schedules.append({
            "시간": time_range,
            "장소": location.strip(),
            "예상 인원": int(expected_people.replace(",", "")),
            "관할서": police_department.strip(),
            "지역": region.strip()
        })

    return schedules

    # pattern = re.compile(
    #     r"(.+?)\n"                         # 장소
    #     r"(\d{1,2}:\d{2}~\d{1,2}:\d{2})\s+"  # 시간
    #     r"([\d,]+)명\s+"                    # 인원 (숫자 + '명')
    #     r"(.+?)\n<(.+?)>",                 # 관할서 + 줄바꿈 + 지역
    #     re.MULTILINE
    # )


    # for match in pattern.findall(text):
    #     print(f"match : {match}")
    #     location, time_range, expected_people, police_department, region = match
    #     schedules.append({
    #         "시간": time_range,
    #         "장소": location.strip(),
    #         "예상 인원": int(expected_people.replace(",", "")),
    #         "관할서": police_department.strip(),
    #         "지역": region.strip()
    #     })
    # return schedules

# ✅ 실행 함수
def main():
    base_url = "https://www.smpa.go.kr/user/nd54882.do"
    
    board_no = get_board_no(base_url)
    if not board_no:
        print("❌ 게시판 번호 가져오기 실패")
        return

    new_url = f"{base_url}?View&uQ=&pageST=SUBJECT&pageSV=&imsi=imsi&page=1&pageSC=SORT_ORDER&pageSO=DESC&dmlType=&boardNo={board_no}&returnUrl=https://www.smpa.go.kr:443/user/nd54882.do"
    file_id, file_name = get_file_id(new_url)
    print(f"file_name : {file_name}")

    if not file_id:
        print("❌ PDF 파일 ID 가져오기 실패")
        return

    # pdf_file = download_file(file_id, f"../data/{file_name}_protest.pdf")
    pdf_file = download_file(file_id, f"./data/{file_name}_protest.pdf")

    
    if pdf_file:
        protest_list = extract_protest_schedule(pdf_file)
        df = pd.DataFrame(protest_list)
        csv_path = f"./data/{file_name}_schedule.csv"
        # csv_path = os.path.join(os.getcwd(), 'data', f"{file_name}_schedule.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"✅ CSV 파일 저장 완료: {csv_path}")

if __name__ == "__main__":
    main()
