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

        if "results" not in data:
            print("⚠️  Unexpected response format")
            return []

        return data["results"]

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []


def update_page_status(page_id, status, properties):
    """페이지의 Published 상태를 업데이트"""
    url = f"https://api.notion.com/v1/pages/{page_id}"

    published_prop = properties.get("Published", {}) or {}
    prop_type = published_prop.get("type", "")

    if prop_type == "status":
        payload = {
            "properties": {
                "Published": {
                    "status": {"name": status}
                }
            }
        }
    elif prop_type == "select":
        payload = {
            "properties": {
                "Published": {
                    "select": {"name": status}
                }
            }
        }
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
    """Notion 블록을 마크다운으로 변환"""
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

            language_map = {
                "plain text": "text",
                "javascript": "javascript",
                "python": "python",
                "java": "java",
                "bash": "bash",
                "shell": "bash",
                "json": "json",
                "yaml": "yaml",
                "yml": "yaml",
                "markdown": "markdown",
                "html": "html",
                "css": "css",
                "sql": "sql",
                "typescript": "typescript",
                "c++": "cpp",
                "c#": "csharp",
                "go": "go",
                "rust": "rust",
                "ruby": "ruby",
                "php": "php",
                "swift": "swift",
                "kotlin": "kotlin",
            }

            language_lower = (language or "text").lower()
            language = language_map.get(language_lower, language_lower.replace(" ", "-"))

            return f"```{language}\n{text}\n```\n\n"

        elif block_type == "quote":
            text = "".join([t["plain_text"] for t in block["quote"]["rich_text"]])
            return f"> {text}\n\n"

        elif block_type == "image":
            if block["image"]["type"] == "external":
                url = block["image"]["external"]["url"]
            else:
                url = block["image"]["file"]["url"]
            caption = "".join([t["plain_text"] for t in block["image"].get("caption", [])])
            return f"![{caption}]({url})\n\n"

        elif block_type == "divider":
            return "\n---\n\n"

        elif block_type == "callout":
            icon = block["callout"].get("icon", {}) or {}
            icon_text = ""
            if icon.get("type") == "emoji":
                icon_text = icon.get("emoji", "💡")

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
    if "Title" in properties:
        title_prop = properties["Title"].get("title", []) or []
        if title_prop:
            return title_prop[0].get("plain_text", "Untitled")

    if "Name" in properties:
        name_prop = properties["Name"].get("title", []) or []
        if name_prop:
            return name_prop[0].get("plain_text", "Untitled")

    for _, prop_data in properties.items():
        if (prop_data or {}).get("type") == "title":
            title_list = (prop_data or {}).get("title", []) or []
            if title_list:
                return title_list[0].get("plain_text", "Untitled")

    return "Untitled"


def get_published_status(properties):
    """Published 상태 가져오기"""
    published_prop = properties.get("Published", {}) or {}

    if published_prop.get("status"):
        return (published_prop["status"] or {}).get("name", "")

    if published_prop.get("select"):
        return (published_prop["select"] or {}).get("name", "")

    return ""


def normalize_date_yyyy_mm_dd(date_str):
    """
    Notion date start는 'YYYY-MM-DD' 또는 'YYYY-MM-DDTHH:MM:SS...' 형태일 수 있음.
    Jekyll 파일명/Front matter date는 일단 'YYYY-MM-DD'만 쓰도록 정규화.
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
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

        # Date
        date_prop = (properties.get("Date") or {}).get("date")
        if date_prop and date_prop.get("start"):
            date_str = normalize_date_yyyy_mm_dd(date_prop["start"])
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # Layout (None-safe)
        layout_prop = properties.get("Layout") or {}
        layout = ((layout_prop.get("select") or {}).get("name")) or "post"

        # Category (None-safe)
        category_prop = properties.get("Category") or {}
        category = ((category_prop.get("select") or {}).get("name")) or ""

        # Tags (None-safe)
        tags_prop = properties.get("Tags") or {}
        tags = [t.get("name") for t in (tags_prop.get("multi_select") or []) if t.get("name")]

        # Author (None-safe)
        author_prop = properties.get("Author") or {}
        author_data = author_prop.get("people") or []
        author = author_data[0].get("name", "") if author_data else ""

        # 본문 내용
        blocks = get_blocks(page["id"])
        content = "".join([notion_block_to_markdown(block) for block in blocks])

        if not content.strip():
            content = "내용을 입력하세요.\n\n"

        # Front Matter
        front_matter_lines = [
            "---",
            f"layout: {layout}",
            f'title: "{title}"',
            f"date: {date_str}",
        ]

        if author:
            front_matter_lines.append(f"author: {author}")

        if category:
            front_matter_lines.append(f"categories: [{category}]")

        if tags:
            front_matter_lines.append(f"tags: {tags}")

        if update_mode:
            front_matter_lines.append(f"last_modified_at: {datetime.now().strftime('%Y-%m-%d')}")

        front_matter_lines.append("---")
        front_matter = "\n".join(front_matter_lines)

        # Front Matter 끝 빈 줄
        full_content = front_matter + "\n\n\n\n" + content

        # 파일명
        safe_title = slugify_title(title)
        filename = f"{date_str}-{safe_title}.md"
        filepath = os.path.join(POSTS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        return filename

    except Exception as e:
        print(f"❌ Error creating post: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)

    stats = {
        "total": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "status_updated": 0,
        "failed": 0,
    }

    for idx, database_id in enumerate(DATABASE_IDS, 1):
        print(f"\n{'='*60}")
        print(f"📚 Database {idx}/{len(DATABASE_IDS)}: {database_id[:8]}...{database_id[-4:]}")
        print(f"{'='*60}")

        pages = get_pages(database_id)

        if not pages:
            print("⚠️  No pages found in this database")
            continue

        print(f"📝 Found {len(pages)} total pages\n")
        stats["total"] += len(pages)

        for page in pages:
            page_id = page["id"]
            properties = page.get("properties", {}) or {}
            title = get_title_from_properties(properties)
            status = get_published_status(properties)

            if status == "Before":
                print(f"🆕 Creating: {title}")
                result = create_jekyll_post(page, update_mode=False)
                if result:
                    stats["created"] += 1
                    print(f"   ✅ Created: {result}")
                    if update_page_status(page_id, "Done", properties):
                        stats["status_updated"] += 1
                    print()
                else:
                    stats["failed"] += 1
                    print()

            elif status == "Need update":
                print(f"🔄 Updating: {title}")
                result = create_jekyll_post(page, update_mode=True)
                if result:
                    stats["updated"] += 1
                    print(f"   ✅ Updated: {result}")
                    if update_page_status(page_id, "Done", properties):
                        stats["status_updated"] += 1
                    print()
                else:
                    stats["failed"] += 1
                    print()

            elif status == "Done":
                print(f"✔️  Already published: {title}")
                stats["skipped"] += 1

            elif status == "In progress":
                print(f"⏳ In progress (skipped): {title}")
                stats["skipped"] += 1

            else:
                print(f"❓ Unknown status '{status}': {title} (skipped)")
                stats["skipped"] += 1

    print(f"\n{'='*60}")
    print("✨ Sync completed!")
    print(f"   Total pages: {stats['total']}")
    print(f"   🆕 Created: {stats['created']}")
    print(f"   🔄 Updated: {stats['updated']}")
    print(f"   ⏭️  Skipped: {stats['skipped']}")
    print(f"   ❌ Failed: {stats['failed']}")
    print(f"   🔄 Status auto-updated: {stats['status_updated']}")
    print(f"{'='*60}")
