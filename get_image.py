import requests
from get_token import get_token

def get_ubuntu_24_image(token):
    # 1. 설정 (본인의 Tenant ID 확인)
    tenant_id = "0cc0040eaa0044bc99f8a7f4bedc233b"
    region_url = "https://kr1-api-image-infrastructure.nhncloudservice.com"
    
    # 2. 이미지 목록 조회 API 호출
    # GET /v2/{tenantId}/images
    url = f"{region_url}/v2/images"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    


    try:
        response = requests.get(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            images = response.json().get("images", [])
            print(f"총 {len(images)}개의 이미지를 조회했습니다.\n")

            # 3. 'Ubuntu'와 '24.04'가 포함된 이미지 찾기 (필터링)
            found = False
            for img in images:
                name = img.get("name", "")
                
                # 대소문자 구분 없이 검색
                if "ubuntu" in name.lower() or "24.04" in name:
                    print(f"✅ 찾은 이미지: {name}")
                    print(f"   ID: {img['id']}")
                    found = True
                    # 하나만 찾고 끝내려면 break, 다 보려면 주석 처리
                    break 
            
            if not found:
                print("❌ 'Ubuntu 24.04' 이미지를 찾을 수 없습니다.")
        else:
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    token_data = get_token()
    if token_data:
        get_ubuntu_24_image(token_data["token_id"])