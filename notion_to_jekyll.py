# notion_to_jekyll.py
import os
import requests
from datetime import datetime

NOTION_TOKEN = os.environ['NOTION_TOKEN']
# 여러 데이터베이스 ID를 쉼표로 구분해서 입력
DATABASE_IDS = os.environ['DATABASE_IDS'].split(',')
POSTS_DIR = '_posts'

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_pages(database_id):
    """특정 데이터베이스에서 페이지 가져오기"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    
    # Published가 "Published" 상태인 것만 필터링
    payload = {
        "filter": {
            "property": "Published",
            "select": {
                "equals": "Published"
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['results']

def get_blocks(page_id):
    """페이지의 블록(내용) 가져오기"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=headers)
    return response.json()['results']

def notion_block_to_markdown(block):
    """Notion 블록을 마크다운으로 변환"""
    block_type = block['type']
    
    if block_type == 'paragraph':
        text = ''.join([t['plain_text'] for t in block['paragraph']['rich_text']])
        return text + '\n\n'
    
    elif block_type == 'heading_1':
        text = ''.join([t['plain_text'] for t in block['heading_1']['rich_text']])
        return f"# {text}\n\n"
    
    elif block_type == 'heading_2':
        text = ''.join([t['plain_text'] for t in block['heading_2']['rich_text']])
        return f"## {text}\n\n"
    
    elif block_type == 'heading_3':
        text = ''.join([t['plain_text'] for t in block['heading_3']['rich_text']])
        return f"### {text}\n\n"
    
    elif block_type == 'bulleted_list_item':
        text = ''.join([t['plain_text'] for t in block['bulleted_list_item']['rich_text']])
        return f"- {text}\n"
    
    elif block_type == 'numbered_list_item':
        text = ''.join([t['plain_text'] for t in block['numbered_list_item']['rich_text']])
        return f"1. {text}\n"
    
    elif block_type == 'code':
        text = ''.join([t['plain_text'] for t in block['code']['rich_text']])
        language = block['code']['language']
        return f"```{language}\n{text}\n```\n\n"
    
    elif block_type == 'quote':
        text = ''.join([t['plain_text'] for t in block['quote']['rich_text']])
        return f"> {text}\n\n"
    
    elif block_type == 'image':
        if block['image']['type'] == 'external':
            url = block['image']['external']['url']
        else:
            url = block['image']['file']['url']
        caption = ''.join([t['plain_text'] for t in block['image'].get('caption', [])])
        return f"![{caption}]({url})\n\n"
    
    return ''

def create_jekyll_post(page):
    """Notion 페이지를 Jekyll 포스트로 변환"""
    properties = page['properties']
    
    # Title
    title = properties['Title']['title'][0]['plain_text'] if properties['Title']['title'] else 'Untitled'
    
    # Date
    date_str = properties.get('Date', {}).get('date', {}).get('start', datetime.now().strftime('%Y-%m-%d'))
    date_str = date_str.replace('/', '-')
    
    # Layout
    layout = properties.get('Layout', {}).get('select', {}).get('name', 'post')
    
    # Category
    category = properties.get('Category', {}).get('select', {}).get('name', '')
    
    # Tags
    tags = [tag['name'] for tag in properties.get('Tags', {}).get('multi_select', [])]
    
    # Author (Person 타입)
    author_data = properties.get('Author', {}).get('people', [])
    author = author_data[0].get('name', '') if author_data else ''
    
    # 본문 내용 가져오기
    blocks = get_blocks(page['id'])
    content = ''.join([notion_block_to_markdown(block) for block in blocks])
    
    # Jekyll Front Matter 생성
    front_matter_lines = [
        "---",
        f"layout: {layout}",
        f'title: "{title}"',
        f"date: {date_str}"
    ]
    
    # Author 추가 (있을 경우)
    if author:
        front_matter_lines.append(f"author: {author}")
    
    # Category 추가 (있을 경우)
    if category:
        front_matter_lines.append(f"categories: [{category}]")
    
    # Tags 추가 (있을 경우)
    if tags:
        front_matter_lines.append(f"tags: {tags}")
    
    front_matter_lines.append("---")
    front_matter = '\n'.join(front_matter_lines) + '\n\n'
    
    # 파일명 생성 (Jekyll 형식: YYYY-MM-DD-title.md)
    safe_title = title.lower().replace(' ', '-').replace('/', '-')
    safe_title = ''.join(c for c in safe_title if c.isalnum() or c == '-')
    filename = f"{date_str}-{safe_title}.md"
    filepath = os.path.join(POSTS_DIR, filename)
    
    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(front_matter + content)
    
    print(f"✅ Created: {filename}")
    return filename

if __name__ == '__main__':
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)
    
    total_pages = 0
    
    # 각 데이터베이스에서 페이지 가져오기
    for idx, database_id in enumerate(DATABASE_IDS, 1):
        database_id = database_id.strip()  # 공백 제거
        print(f"\n📚 Database {idx}/{len(DATABASE_IDS)}")
        print(f"🔄 Fetching pages from: {database_id[:8]}...{database_id[-4:]}")
        
        try:
            pages = get_pages(database_id)
            print(f"📝 Found {len(pages)} published pages")
            total_pages += len(pages)
            
            # 각 페이지를 Jekyll 포스트로 변환
            for page in pages:
                try:
                    create_jekyll_post(page)
                except Exception as e:
                    title = page['properties']['Title']['title'][0]['plain_text'] if page['properties']['Title']['title'] else 'Unknown'
                    print(f"❌ Error processing '{title}': {str(e)}")
        
        except Exception as e:
            print(f"❌ Error fetching from database {database_id}: {str(e)}")
    
    print(f"\n✨ Sync completed! Total: {total_pages} pages processed")
