# notion_to_jekyll.py
import os
import requests
from datetime import datetime
import json

NOTION_TOKEN = os.environ['NOTION_TOKEN']
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
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # HTTP 에러 체크
        
        data = response.json()
        
        # 에러 응답 체크
        if 'object' in data and data['object'] == 'error':
            print(f"❌ Notion API Error: {data.get('message', 'Unknown error')}")
            return []
        
        # results 키 확인
        if 'results' not in data:
            print(f"⚠️  Unexpected response format: {json.dumps(data, indent=2)}")
            return []
        
        return data['results']
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return []

def get_blocks(page_id):
    """페이지의 블록(내용) 가져오기"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'results' not in data:
            print(f"⚠️  No blocks found for page {page_id}")
            return []
        
        return data['results']
    
    except Exception as e:
        print(f"❌ Error fetching blocks: {str(e)}")
        return []

def notion_block_to_markdown(block):
    """Notion 블록을 마크다운으로 변환"""
    block_type = block.get('type', '')
    
    try:
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
            language = block['code'].get('language', '')
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
    
    except Exception as e:
        print(f"⚠️  Error converting block type '{block_type}': {str(e)}")
    
    return ''

def create_jekyll_post(page):
    """Notion 페이지를 Jekyll 포스트로 변환"""
    try:
        properties = page['properties']
        
        # Title
        title_prop = properties.get('Title', {}).get('title', [])
        title = title_prop[0]['plain_text'] if title_prop else 'Untitled'
        
        # Date
        date_prop = properties.get('Date', {}).get('date')
        if date_prop and date_prop.get('start'):
            date_str = date_prop['start'].replace('/', '-')
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Layout
        layout = properties.get('Layout', {}).get('select', {}).get('name', 'post')
        
        # Category
        category = properties.get('Category', {}).get('select', {}).get('name', '')
        
        # Tags
        tags = [tag['name'] for tag in properties.get('Tags', {}).get('multi_select', [])]
        
        # Author
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
        
        if author:
            front_matter_lines.append(f"author: {author}")
        
        if category:
            front_matter_lines.append(f"categories: [{category}]")
        
        if tags:
            front_matter_lines.append(f"tags: {tags}")
        
        front_matter_lines.append("---")
        front_matter = '\n'.join(front_matter_lines) + '\n\n'
        
        # 파일명 생성
        safe_title = title.lower().replace(' ', '-').replace('/', '-')
        safe_title = ''.join(c for c in safe_title if c.isalnum() or c == '-')
        filename = f"{date_str}-{safe_title}.md"
        filepath = os.path.join(POSTS_DIR, filename)
        
        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter + content)
        
        print(f"✅ Created: {filename}")
        return filename
    
    except Exception as e:
        print(f"❌ Error creating post: {str(e)}")
        return None

if __name__ == '__main__':
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)
    
    total_pages = 0
    
    # 각 데이터베이스에서 페이지 가져오기
    for idx, database_id in enumerate(DATABASE_IDS, 1):
        database_id = database_id.strip()
        print(f"\n📚 Database {idx}/{len(DATABASE_IDS)}")
        print(f"🔄 Fetching pages from: {database_id[:8]}...{database_id[-4:]}")
        
        pages = get_pages(database_id)
        
        if not pages:
            print(f"⚠️  No published pages found in this database")
            continue
        
        print(f"📝 Found {len(pages)} published pages")
        total_pages += len(pages)
        
        for page in pages:
            create_jekyll_post(page)
    
    print(f"\n✨ Sync completed! Total: {total_pages} pages processed")
