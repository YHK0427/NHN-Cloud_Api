import requests
import json
from get_token import get_token

def list_key_pairs(token: str, tenant_id: str, region_code: str = "kr1"):
    """
    키페어 목록을 조회하는 함수
    API: GET /v2/{tenantId}/os-keypairs
    """
    COMPUTE_API_URL = f"https://{region_code}-api-compute-infrastructure.nhncloudservice.com"
    url = f"{COMPUTE_API_URL}/v2/{tenant_id}/os-keypairs"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200:
            keypairs_data = response.json().get('keypairs', [])
            print(f"✅ 키페어 목록 조회 성공! (Region: {region_code})")
            if keypairs_data:
                key_pair_list = []
                for kp in keypairs_data:
                    keypair_info = kp.get('keypair', {})
                    key_pair_list.append({
                        "name": keypair_info.get('name'),
                        "fingerprint": keypair_info.get('fingerprint')
                    })
                    print(f" - 이름: {keypair_info.get('name')}, 지문: {keypair_info.get('fingerprint')}")
                return key_pair_list
            else:
                print(" - 등록된 키페어가 없습니다.")
                return []
        else:
            print(f"❌ 키페어 목록 조회 실패 (Status: {response.status_code})")
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
    # create_vpc.py 에서 사용했던 TENANT_ID를 가정합니다.
    example_tenant_id = "0cc0040eaa0044bc99f8a7f4bedc233b" # 실제 테넌트 ID로 변경!
    
    if example_tenant_id == "YOUR_TENANT_ID_HERE" or example_tenant_id == "0cc0040eaa0044bc99f8a7f4bedc233b":
        print("⚠️ 경고: 'example_tenant_id'를 실제 테넌트 ID로 변경해주세요!")
        print("    NHN Cloud 콘솔에서 테넌트 ID를 확인하거나, get_token 응답에서 'access.token.tenant.id' 값을 확인할 수 있습니다.")
    else:
        # 3. 키페어 목록 조회 시도
        key_pairs = list_key_pairs(auth_token, example_tenant_id, "kr1")

        if key_pairs is not None:
            if key_pairs:
                print("✨ 사용 가능한 키페어 목록:")
                for kp in key_pairs:
                    print(f"  - 이름: {kp['name']}, 지문: {kp['fingerprint']}")
            else:
                print("✨ 사용 가능한 키페어가 없습니다.")
        else:
            print("🚨 키페어 목록 조회에 실패했습니다.")
