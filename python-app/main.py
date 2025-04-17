from demon_tracker import get_board_no, get_file_id, download_file


def generate_new_url(url, board_no):
    """board_no를 사용해 새 URL 생성"""
    return f"{url}?View&uQ=&pageST=SUBJECT&pageSV=&imsi=imsi&page=1&pageSC=SORT_ORDER&pageSO=DESC&dmlType=&boardNo={board_no}&returnUrl=https://www.smpa.go.kr:443/user/nd54882.do"


def main():
    url = 'https://www.smpa.go.kr/user/nd54882.do'

    # 1. 게시판 번호 가져오기
    board_no = get_board_no(url)
    if not board_no:
        print("Failed to retrieve board number.")
        return

    # 2. 새로운 URL 생성 및 파일 정보 가져오기
    new_url = generate_new_url(url, board_no)
    file_id, file_name = get_file_id(new_url)
    if not (file_id and file_name):
        print("Failed to retrieve file ID or file name.")
        return

    # 3. 파일 다운로드
    if download_file(file_id, file_name):
        print("File downloaded successfully.")
    else:
        print("Failed to download file.")


if __name__ == "__main__":
    main()
