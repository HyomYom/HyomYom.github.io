# notion_to_jekyll.py
import os
import requests
from datetime import datetime
import glob

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_IDS = [db_id.strip().replace("-", "") for db_id in os.environ["DATABASE_IDS"].split(",")]
POSTS_DIR = "_posts"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def get_pages(database_id):
    """특정 데이터베이스에서 페이지 가져오기"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"❌ Response: {response.text}")
            response.raise_for_status()
        data = response.json()
        if data.get("object") == "error":
            print(f"❌ Notion API Error: {data.get('message', 'Unknown error')}")
            return []
        return data.get("results", [])
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def update_page_status(page_id, status, properties):
    """페이지의 Published 상태를 업데이트"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    published_prop = properties.get("Published", {}) or {}
    prop_type = published_prop.get("type", "")

    if prop_type == "status":
        payload = {"properties": {"Published": {"status": {"name": status}}}}
    elif prop_type == "select":
        payload = {"properties": {"Published": {"select": {"name": status}}}}
    else:
        print(f"   ⚠️  Unknown Published property type: {prop_type}")
        return False

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
        return data.get("results", []) or []
    except Exception as e:
        print(f"❌ Error fetching blocks: {str(e)}")
        return []

def notion_block_to_markdown(block):
    """Notion 블록을 마크다운으로 변환 (기존 로직 유지)"""
    block_type = block.get("type", "")
    try:
        if block_type == "paragraph":
            text = "".join([t["plain_text"] for t in block["paragraph"]["rich_text"]])
            return text + "\n\n"
        elif block_type == "heading_1":
            text = "".join([t["plain_text"] for t in block["heading_1"]["rich_text"]])
            return f"# {text}\n\n"
        elif block_type == "heading_2":
            text = "".join([t["plain_text"] for t in block["heading_2"]["rich_text"]])
            return f"## {text}\n\n"
        elif block_type == "heading_3":
            text = "".join([t["plain_text"] for t in block["heading_3"]["rich_text"]])
            return f"### {text}\n\n"
        elif block_type == "bulleted_list_item":
            text = "".join([t["plain_text"] for t in block["bulleted_list_item"]["rich_text"]])
            return f"- {text}\n"
        elif block_type == "numbered_list_item":
            text = "".join([t["plain_text"] for t in block["numbered_list_item"]["rich_text"]])
            return f"1. {text}\n"
        elif block_type == "code":
            text = "".join([t["plain_text"] for t in block["code"]["rich_text"]])
            language = block["code"].get("language", "text")
            return f"```{language}\n{text}\n```\n\n"
        elif block_type == "quote":
            text = "".join([t["plain_text"] for t in block["quote"]["rich_text"]])
            return f"> {text}\n\n"
        elif block_type == "image":
            url = block["image"]["external"]["url"] if block["image"]["type"] == "external" else block["image"]["file"]["url"]
            caption = "".join([t["plain_text"] for t in block["image"].get("caption", [])])
            return f"![{caption}]({url})\n\n"
        elif block_type == "divider":
            return "\n---\n\n"
        elif block_type == "callout":
            icon = block["callout"].get("icon", {}) or {}
            icon_text = icon.get("emoji", "💡") if icon.get("type") == "emoji" else ""
            text = "".join([t["plain_text"] for t in block["callout"]["rich_text"]])
            return f"> {icon_text} {text}\n\n"
        elif block_type == "toggle":
            text = "".join([t["plain_text"] for t in block["toggle"]["rich_text"]])
            return f"<details>\n<summary>{text}</summary>\n\n</details>\n\n"
    except Exception as e:
        print(f"⚠️  Error converting block type '{block_type}': {str(e)}")
    return ""

def get_title_from_properties(properties):
    """Title 또는 Name 속성에서 제목 추출"""
    for key in ["Title", "Name"]:
        if key in properties:
            title_prop = properties[key].get("title", [])
            if title_prop: return title_prop[0].get("plain_text", "Untitled")
    for _, prop_data in properties.items():
        if (prop_data or {}).get("type") == "title":
            title_list = (prop_data or {}).get("title", [])
            if title_list: return title_list[0].get("plain_text", "Untitled")
    return "Untitled"

def get_published_status(properties):
    """Published 상태 가져오기"""
    published_prop = properties.get("Published", {}) or {}
    for key in ["status", "select"]:
        if published_prop.get(key):
            return (published_prop[key] or {}).get("name", "")
    return ""

def normalize_date_yyyy_mm_dd(date_str):
    if not date_str: return datetime.now().strftime("%Y-%m-%d")
    return str(date_str)[:10]

def slugify_title(title):
    safe_title = (title or "").lower().replace(" ", "-").replace("/", "-")
    safe_title = "".join(c for c in safe_title if c.isalnum() or c == "-")
    safe_title = "-".join(filter(None, safe_title.split("-")))
    return safe_title or "untitled"

def create_jekyll_post(page, update_mode=False):
    """Notion 페이지를 Jekyll 포스트로 변환"""
    try:
        properties = page.get("properties", {}) or {}
        title = get_title_from_properties(properties)
        date_prop = (properties.get("Date") or {}).get("date")
        date_str = normalize_date_yyyy_mm_dd(date_prop["start"]) if date_prop else datetime.now().strftime("%Y-%m-%d")

        layout = ((properties.get("Layout", {}).get("select") or {}).get("name")) or "post"
        category = ((properties.get("Category", {}).get("select") or {}).get("name")) or ""
        tags = [t.get("name") for t in (properties.get("Tags", {}).get("multi_select") or []) if t.get("name")]
        author_data = properties.get("Author", {}).get("people") or []
        author = author_data[0].get("name", "") if author_data else ""

        blocks = get_blocks(page["id"])
        content = "".join([notion_block_to_markdown(block) for block in blocks]) or "내용을 입력하세요.\n\n"

        front_matter = [
            "---", f"layout: {layout}", f'title: "{title}"', f"date: {date_str}"
        ]
        if author: front_matter.append(f"author: {author}")
        if category: front_matter.append(f"categories: [{category}]")
        if tags: front_matter.append(f"tags: {tags}")
        if update_mode: front_matter.append(f"last_modified_at: {datetime.now().strftime('%Y-%m-%d')}")
        front_matter.append("---\n\n\n\n")

        full_content = "\n".join(front_matter) + content
        filename = f"{date_str}-{slugify_title(title)}.md"
        
        target_dir = POSTS_DIR
        if category:
            category_dir = os.path.join(POSTS_DIR, category)
            if os.path.isdir(category_dir): target_dir = category_dir

        filepath = os.path.join(target_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        return filename
    except Exception as e:
        print(f"❌ Error creating post: {str(e)}")
        return None

def delete_jekyll_post(page):
    """Status가 'Delete'인 경우 로컬 파일 삭제"""
    try:
        properties = page.get("properties", {}) or {}
        title = get_title_from_properties(properties)
        date_prop = (properties.get("Date") or {}).get("date")
        date_str = normalize_date_yyyy_mm_dd(date_prop["start"]) if date_prop else None
        
        if not date_str:
            print(f"   ⚠️  Cannot determine date for: {title}")
            return False

        filename = f"{date_str}-{slugify_title(title)}.md"
        # _posts 폴더 및 하위 폴더 전체에서 해당 파일명을 검색
        search_pattern = os.path.join(POSTS_DIR, "**", filename)
        found_files = glob.glob(search_pattern, recursive=True)

        if not found_files:
            print(f"   ⚠️  File not found on local: {filename}")
            return True # 파일이 없어도 성공으로 간주 (이미 삭제됨)

        for filepath in found_files:
            os.remove(filepath)
            print(f"   🗑️  Deleted: {filepath}")
        return True
    except Exception as e:
        print(f"   ❌ Error deleting file: {str(e)}")
        return False


if __name__ == "__main__":
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)

    stats = {
        "total": 0, "created": 0, "updated": 0, 
        "deleted": 0, "skipped": 0, "status_updated": 0, "failed": 0,
    }

    for idx, database_id in enumerate(DATABASE_IDS, 1):
        print(f"\n{'='*60}\n📚 Database {idx}: {database_id[:8]}...\n{'='*60}")
        pages = get_pages(database_id)
        if not pages: continue
        stats["total"] += len(pages)

        for page in pages:
            page_id = page["id"]
            properties = page.get("properties", {}) or {}
            title = get_title_from_properties(properties)
            status = get_published_status(properties)

            if status == "Before":
                print(f"🆕 Creating: {title}")
                if create_jekyll_post(page):
                    stats["created"] += 1
                    if update_page_status(page_id, "Done", properties): stats["status_updated"] += 1
                else: stats["failed"] += 1

            elif status == "Need update":
                print(f"🔄 Updating: {title}")
                if create_jekyll_post(page, update_mode=True):
                    stats["updated"] += 1
                    if update_page_status(page_id, "Done", properties): stats["status_updated"] += 1
                else: stats["failed"] += 1

            elif status == "Delete":
                print(f"🗑️  Action: Delete -> {title}")
                if delete_jekyll_post(page):
                    stats["deleted"] += 1
                    # 삭제 완료 후 상태를 'Deleted'로 변경하여 다시 처리되지 않게 함
                    if update_page_status(page_id, "Deleted", properties): stats["status_updated"] += 1
                else: stats["failed"] += 1

            elif status in ["Done", "In progress", "Deleted"]:
                print(f"✔️  Skipped ({status}): {title}")
                stats["skipped"] += 1
            else:
                print(f"❓ Unknown status '{status}': {title}")
                stats["skipped"] += 1

    print(f"\n{'='*60}\n✨ Sync completed!\n"
          f"   Total: {stats['total']} | 🆕 New: {stats['created']} | 🔄 Upd: {stats['updated']}\n"
          f"   🗑️  Del: {stats['deleted']} | ⏭️  Skip: {stats['skipped']} | ❌ Fail: {stats['failed']}\n{'='*60}")
