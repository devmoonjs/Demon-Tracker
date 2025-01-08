import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

# 최상단 게시판 번호 가져오기
def get_board_no(url):
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select_one('#subContents > div > div.inContent > table > tbody > tr:nth-child(1) > td.subject > a')
        

        match = re.search(r"goBoardView\(.+,'View','(\d+)'\)", str(title))
        if match:
            return match.group(1)
    return None

# 하이퍼링크 내부 다운 받을 파일 번호 가져오기
import requests
from bs4 import BeautifulSoup
import re


def get_file_id(new_url):
    try:
        # HTTP 요청
        response = requests.get(new_url)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link = soup.select_one('#subContents > div > div.inContent > table > tbody > tr:nth-child(3) > td > a:nth-child(3)')
        print(link)

        today_text = link.get_text(strip=True)
        extracted_day = extract_number_from_text(today_text)
        today_demon_file_id = extract_demon_file_id(link)

        print("Extracted Day : ", extracted_day)
        print("File ID : ", today_demon_file_id)

        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%y%m%d")
        print("Date Time : ", tomorrow_date)
        
        if(check_demon_file(extracted_day, tomorrow_date)):
            return today_demon_file_id, extracted_day
        return None
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def check_demon_file(extracted_day, tomorrow_date):
    """내일 집회 공지 파일이 맞는지 체크"""
    return extracted_day == tomorrow_date

def extract_number_from_text(text):
    """텍스트에서 숫자를 추출하는 함수"""
    match = re.search(r'(\d+)', text)
    return match.group(1) if match else None


def extract_demon_file_id(link_element):
    """파일 ID를 추출하는 함수"""
    match = re.search(r"attachfileDownload\('.+','(\d+)'\)", str(link_element))
    return match.group(1) if match else None


# 오늘의 시위 일정 pdf 다운로드
def download_file(file_id, file_name):
    url = f"https://www.smpa.go.kr/common/attachfile/attachfileDownload.do?attachNo={file_id}"
    response = requests.get(url)
    if response.status_code == 200:
        file_name += ".pdf"
        with open(file_name, "wb") as f:
            f.write(response.content)
        return True
    return False
