import os
import requests
from datetime import datetime

# 1. 환경 변수 설정
NOTION_TOKEN = os.environ['NOTION_TOKEN']
# 여러 ID를 쉼표(,)로 구분해서 넣을 예정입니다. 예: "id1,id2,id3"
DATABASE_IDS = [i.strip() for i in os.environ['NOTION_DATABASE_ID'].split(',')]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_pages(db_id):
    """특정 DB에서 'Before' 상태인 글만 가져오기"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    filter_data = {
        "filter": {
            "property": "Published",
            "select": {"equals": "Before"} #
        }
    }
    res = requests.post(url, headers=headers, json=filter_data)
    return res.json().get("results", [])

def update_status(page_id):
    """작업 완료 후 노션 상태를 'Done'으로 변경"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {"properties": {"Published": {"select": {"name": "Done"}}}}
    requests.patch(url, headers=headers, json=data)

def sync():
    for db_id in DATABASE_IDS:
        print(f"Checking Database: {db_id}")
        pages = get_pages(db_id)
        
        for page in pages:
            props = page["properties"]
            title = props["Name"]["title"][0]["plain_text"]
            category = props["Category"]["select"]["name"] #
            
            # (파일 저장 로직 생략: 이전과 동일하게 _posts 폴더에 저장)
            print(f" - Found new post: {title}")
            
            # 상태 업데이트
            update_status(page["id"])
            print(f" - Status updated to 'Done' for: {title}")

if __name__ == "__main__":
    sync()
