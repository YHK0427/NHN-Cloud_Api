import requests
import json
from get_token import get_token

def list_flavors(token: str, tenant_id: str, region_code: str = "kr1", min_disk: int = None, min_ram: int = None):
    """
    인스턴스 타입(플레이버) 목록을 조회하는 함수
    API: GET /v2/{tenantId}/flavors
    """
    COMPUTE_API_URL = f"https://{region_code}-api-instance-infrastructure.nhncloudservice.com"
    url = f"{COMPUTE_API_URL}/v2/{tenant_id}/flavors"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    params = {}
    if min_disk is not None:
        params["minDisk"] = min_disk
    if min_ram is not None:
        params["minRam"] = min_ram

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200:
            flavors_data = response.json().get('flavors', [])
            print(f"✅ 플레이버 목록 조회 성공! (Region: {region_code})")
            if flavors_data:
                flavor_list = []
                for f in flavors_data:
                    flavor_list.append({
                        "id": f.get('id'),
                        "name": f.get('name')
                    })
                    print(f" - 이름: {f.get('name')}, ID: {f.get('id')}")
                return flavor_list
            else:
                print(" - 조회된 플레이버가 없습니다.")
                return []
        else:
            print(f"❌ 플레이버 목록 조회 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]

    # 2. 테넌트 ID (NHN Cloud 콘솔 등에서 확인 필요)
    example_tenant_id = "0cc0040eaa0044bc99f8a7f4bedc233b" # 실제 테넌트 ID로 변경!
    
    if example_tenant_id == "YOUR_TENANT_ID_HERE" or example_tenant_id == "0cc0040eaa0044bc99f8a7f4bedc233b":
        print("⚠️ 경고: 'example_tenant_id'를 실제 테넌트 ID로 변경해주세요!")
        print("    NHN Cloud 콘솔에서 테넌트 ID를 확인하거나, get_token 응답에서 'access.token.tenant.id' 값을 확인할 수 있습니다.")
    else:
        # 3. 플레이버 목록 조회 시도
        print("--- 모든 플레이버 목록 ---")
        flavors = list_flavors(auth_token, example_tenant_id, "kr1")

        if flavors is not None:
            if flavors:
                print("✨ 사용 가능한 플레이버 목록:")
                for f in flavors:
                    print(f"  - 이름: {f['name']}, ID: {f['id']}")
            else:
                print("✨ 사용 가능한 플레이버가 없습니다.")
        else:
            print("🚨 플레이버 목록 조회에 실패했습니다.")
        
        print("--- 최소 RAM 2GB 이상 플레이버 목록 ---")
        flavors_2gb_ram = list_flavors(auth_token, example_tenant_id, "kr1", min_ram=2048) # 2GB = 2048MB
        if flavors_2gb_ram is not None:
            if flavors_2gb_ram:
                print("✨ 사용 가능한 2GB RAM 이상 플레이버 목록:")
                for f in flavors_2gb_ram:
                    print(f"  - 이름: {f['name']}, ID: {f['id']}")
