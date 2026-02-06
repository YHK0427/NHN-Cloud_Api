import requests
import json

def create_internet_gateway(token: str, ig_name: str, external_network_id: str, region_code: str = "kr1"):
    """
    인터넷 게이트웨이를 생성하는 함수
    API: POST /v2.0/internetgateways
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/internetgateways"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "internetgateway": {
            "name": ig_name,
            "external_network_id": external_network_id
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 4xx or 5xx 에러 발생 시 예외 처리
        
        if response.status_code == 201: # 201 Created for successful creation
            ig_info = response.json().get('internetgateway', {})
            print(f"✅ 인터넷 게이트웨이 '{ig_name}' 생성 성공! (ID: {ig_info.get('id')}, Region: {region_code})")
            return ig_info.get('id')
        else:
            print(f"❌ 인터넷 게이트웨이 '{ig_name}' 생성 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        print(f"❗ HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return None

if __name__ == '__main__':
    from get_token import get_token
    from get_external_network_id import get_external_network_id
    
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]
    
    # 2. 외부 네트워크 ID 가져오기 (이미 main.py에 있는 로직 활용)
    external_net_id = get_external_network_id(auth_token, "kr1")

    # 3. 인터넷 게이트웨이 이름 설정
    ig_test_name = "my-test-ig"

    if auth_token and external_net_id:
        print(f"외부 네트워크 ID: {external_net_id}")
        ig_id = create_internet_gateway(auth_token, ig_test_name, external_net_id, "kr1")
        if ig_id:
            print(f"✨ 생성된 인터넷 게이트웨이 ID: {ig_id}")
        else:
            print("🚨 인터넷 게이트웨이 생성 실패.")
    else:
        print("인증 토큰 또는 외부 네트워크 ID를 가져오지 못했습니다.")