# notion_to_jekyll.py
import os
import requests
from datetime import datetime
import glob

NOTION_TOKEN = os.environ['NOTION_TOKEN']
DATABASE_IDS = [db_id.strip().replace('-', '') for db_id in os.environ['DATABASE_IDS'].split(',')]
POSTS_DIR = '_posts'

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_pages(database_id):
    """특정 데이터베이스에서 페이지 가져오기"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    
    # 모든 페이지 가져오기 (필터 없음)
    payload = {}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ Response: {response.text}")
            response.raise_for_status()
        
        data = response.json()
        
        if 'object' in data and data['object'] == 'error':
            print(f"❌ Notion API Error: {data.get('message', 'Unknown error')}")
            return []
        
        if 'results' not in data:
            print(f"⚠️  Unexpected response format")
            return []
        
        return data['results']
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def update_page_status(page_id, status):
    """페이지의 Published 상태를 업데이트"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {
        "properties": {
            "Published": {
                "select": {
                    "name": status
                }
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"   ✅ Status updated to: {status}")
            return True
        else:
            print(f"   ⚠️  Failed to update status: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ⚠️  Error updating status: {str(e)}")
        return False

def get_blocks(page_id):
    """페이지의 블록(내용) 가져오기"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'results' not in data:
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
        
        elif block_type == 'divider':
            return "---\n\n"
        
        elif block_type == 'callout':
            text = ''.join([t['plain_text'] for t in block['callout']['rich_text']])
            return f"> 💡 {text}\n\n"
    
    except Exception as e:
        print(f"⚠️  Error converting block type '{block_type}': {str(e)}")
    
    return ''

def get_title_from_properties(properties):
    """Title 또는 Name 속성에서 제목 추출"""
    if 'Title' in properties:
        title_prop = properties['Title'].get('title', [])
        if title_prop:
            return title_prop[0]['plain_text']
    
    if 'Name' in properties:
        name_prop = properties['Name'].get('title', [])
        if name_prop:
            return name_prop[0]['plain_text']
    
    for prop_name, prop_data in properties.items():
        if prop_data.get('type') == 'title':
            title_list = prop_data.get('title', [])
            if title_list:
                return title_list[0]['plain_text']
    
    return 'Untitled'

def get_published_status(properties):
    """Published 상태 가져오기"""
    published_prop = properties.get('Published', {})
    
    # Select 타입
    if 'select' in published_prop and published_prop['select']:
        return published_prop['select'].get('name', '')
    
    # Status 타입
    if 'status' in published_prop and published_prop['status']:
        return published_prop['status'].get('name', '')
    
    return ''

def find_existing_post(title, date_str):
    """기존 포스트 파일 찾기"""
    safe_title = title.lower().replace(' ', '-').replace('/', '-')
    safe_title = ''.join(c for c in safe_title if c.isalnum() or c == '-')
    
    # 정확한 파일명으로 찾기
    exact_file = os.path.join(POSTS_DIR, f"{date_str}-{safe_title}.md")
    if os.path.exists(exact_file):
        return exact_file
    
    # 제목으로 검색 (날짜가 다를 수 있음)
    pattern = os.path.join(POSTS_DIR, f"*-{safe_title}.md")
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    
    return None

def create_jekyll_post(page, update_mode=False):
    """Notion 페이지를 Jekyll 포스트로 변환"""
    try:
        properties = page['properties']
        
        title = get_title_from_properties(properties)
        
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
        
        # 업데이트 모드면 last_modified 추가
        if update_mode:
            front_matter_lines.append(f"last_modified_at: {datetime.now().strftime('%Y-%m-%d')}")
        
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
        
        return filename
    
    except Exception as e:
        print(f"❌ Error creating post: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)
    
    stats = {
        'total': 0,
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'status_updated': 0
    }
    
    for idx, database_id in enumerate(DATABASE_IDS, 1):
        print(f"\n{'='*60}")
        print(f"📚 Database {idx}/{len(DATABASE_IDS)}: {database_id[:8]}...{database_id[-4:]}")
        print(f"{'='*60}")
        
        pages = get_pages(database_id)
        
        if not pages:
            print(f"⚠️  No pages found in this database")
            continue
        
        print(f"📝 Found {len(pages)} total pages\n")
        stats['total'] += len(pages)
        
        for page in pages:
            page_id = page['id']
            properties = page['properties']
            title = get_title_from_properties(properties)
            status = get_published_status(properties)
            
            # 상태별 처리
            if status == 'Before':
                # 새로 포스팅
                print(f"🆕 Creating: {title}")
                result = create_jekyll_post(page, update_mode=False)
                if result:
                    stats['created'] += 1
                    print(f"   ✅ Created: {result}")
                    # 상태를 Done으로 변경
                    if update_page_status(page_id, 'Done'):
                        stats['status_updated'] += 1
                    print()
            
            elif status == 'Need update':
                # 기존 포스트 업데이트
                print(f"🔄 Updating: {title}")
                result = create_jekyll_post(page, update_mode=True)
                if result:
                    stats['updated'] += 1
                    print(f"   ✅ Updated: {result}")
                    # 상태를 Done으로 변경
                    if update_page_status(page_id, 'Done'):
                        stats['status_updated'] += 1
                    print()
            
            elif status == 'Done':
                # 이미 완료된 것, 건드리지 않음
                print(f"✔️  Already published: {title}")
                stats['skipped'] += 1
            
            elif status == 'In progress':
                # 작업 중, 건드리지 않음
                print(f"⏳ In progress (skipped): {title}")
                stats['skipped'] += 1
            
            else:
                # 상태가 없거나 알 수 없는 상태
                print(f"❓ Unknown status '{status}': {title} (skipped)")
                stats['skipped'] += 1
    
    print(f"\n{'='*60}")
    print(f"✨ Sync completed!")
    print(f"   Total pages: {stats['total']}")
    print(f"   🆕 Created: {stats['created']}")
    print(f"   🔄 Updated: {stats['updated']}")
    print(f"   ⏭️  Skipped: {stats['skipped']}")
    print(f"   🔄 Status auto-updated: {stats['status_updated']}")
    print(f"{'='*60}")
