import requests
import json
from get_token import get_token

def create_vpc_subnet(token: str, vpc_id: str, subnet_name: str, cidr: str, region_code: str = "kr1"):
    """
    VPC 서브넷을 생성하는 함수
    API: POST /v2.0/vpcsubnets
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/vpcsubnets"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "vpcsubnet": {
            "vpc_id": vpc_id,
            "cidr": cidr,
            "name": subnet_name
            # "tenant_id": "" # Optional, if not provided, it uses the token's tenant_id
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200 or response.status_code == 201: # Assuming 200 OK for successful creation as per the doc, though 201 Created is more common for resource creation.
            subnet_info = response.json().get('vpcsubnet', {})
            print(f"✅ VPC 서브넷 생성 성공! (Region: {region_code})")
            print(f" - 이름: {subnet_info.get('name')}")
            print(f" - ID: {subnet_info.get('id')}")
            print(f" - CIDR: {subnet_info.get('cidr')}")
            print(f" - VPC ID: {subnet_info.get('vpc_id')}")
            return subnet_info.get('id')
        else:
            # This part might be redundant due to raise_for_status, but good for explicit handling
            print(f"❌ VPC 서브넷 생성 실패 (Status: {response.status_code})")
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
    # 이 부분은 테스트를 위한 예시 코드입니다.
    # 실제 VPC ID와 서브넷 정보를 사용해야 합니다.
    
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]

    # 2. VPC 서브넷 생성 시도
    # 예시: 기존 VPC ID와 새로운 서브넷 정보 사용
    # 이 VPC ID는 이전에 create_vpc.py를 통해 생성된 VPC의 ID입니다.
    # 실제 사용 시 유효한 VPC ID로 교체해주세요.
    example_vpc_id = "f8cb3c08-c233-4438-8d16-98155468fb3e"  # 실제 VPC ID로 변경해야 함!
    subnet_name = "python-subnet"
    subnet_cidr = "10.0.1.0/24" # VPC CIDR 범위 내에 있어야 함 (예: 10.0.0.0/16 VPC 안)
    
    if example_vpc_id == "YOUR_VPC_ID_HERE":
        print("⚠️ 경고: 'example_vpc_id'를 실제 VPC ID로 변경해주세요!")
        print("먼저 create_vpc.py를 실행하여 VPC를 생성하고 ID를 확인하세요.")
    else:
        created_subnet_id = create_vpc_subnet(auth_token, example_vpc_id, subnet_name, subnet_cidr, "kr1")

        if created_subnet_id:
            print(f"✨ 최종적으로 생성된 서브넷 ID: {created_subnet_id}")
        else:
            print("🚨 서브넷 생성에 실패했습니다.")
