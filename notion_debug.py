# notion_debug.py
import os
import requests
import json

NOTION_TOKEN = os.environ.get('NOTION_TOKEN', '')
DATABASE_IDS_RAW = os.environ.get('DATABASE_IDS', '')

print("=" * 60)
print("🔍 DEBUGGING NOTION CONNECTION")
print("=" * 60)

# 토큰 확인
if not NOTION_TOKEN:
    print("❌ NOTION_TOKEN이 설정되지 않았습니다!")
else:
    print(f"✅ NOTION_TOKEN: {NOTION_TOKEN[:20]}...{NOTION_TOKEN[-10:]}")

# Database IDs 확인
print(f"\n📋 Raw DATABASE_IDS: {DATABASE_IDS_RAW}")

DATABASE_IDS = [db_id.strip().replace('-', '') for db_id in DATABASE_IDS_RAW.split(',')]
print(f"📋 Parsed DATABASE_IDS: {DATABASE_IDS}")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

print("\n" + "=" * 60)
print("🧪 TESTING DATABASE ACCESS")
print("=" * 60)

for idx, db_id in enumerate(DATABASE_IDS, 1):
    print(f"\n📚 Testing Database {idx}: {db_id}")
    
    # 32자 확인
    if len(db_id) != 32:
        print(f"⚠️  WARNING: ID length is {len(db_id)}, should be 32")
    
    # API 호출
    url = f"https://api.notion.com/v1/databases/{db_id}"
    print(f"🔗 URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Database title: {data.get('title', [{}])[0].get('plain_text', 'No title')}")
            
            # 속성 확인
            properties = data.get('properties', {})
            print(f"📝 Properties found: {list(properties.keys())}")
            
        elif response.status_code == 404:
            print(f"❌ 404 NOT FOUND")
            print("   가능한 원인:")
            print("   1. Database ID가 잘못됨")
            print("   2. Integration이 이 데이터베이스에 연결되지 않음")
            
        elif response.status_code == 401:
            print(f"❌ 401 UNAUTHORIZED")
            print("   NOTION_TOKEN이 유효하지 않습니다")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print("\n" + "=" * 60)
print("💡 다음 단계:")
print("=" * 60)
print("1. Notion에서 데이터베이스 페이지를 full page로 열기")
print("2. 브라우저 주소창 URL 전체 복사")
print("3. Integration 연결 확인:")
print("   - 데이터베이스 우측 상단 ... 클릭")
print("   - 'Connections' 클릭")
print("   - Integration이 보이면 ✅, 없으면 'Add connections'로 추가")
