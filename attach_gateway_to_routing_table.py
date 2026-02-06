import requests
import json

def attach_gateway_to_routing_table(token: str, routing_table_id: str, internet_gateway_id: str, region_code: str = "kr1"):
    """
    라우팅 테이블에 인터넷 게이트웨이를 연결하는 함수
    API: PUT /v2.0/routingtables/{routingtableId}/attach_gateway
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/routingtables/{routing_table_id}/attach_gateway"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "gateway_id": internet_gateway_id
    }
    
    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 4xx or 5xx 에러 발생 시 예외 처리
        
        if response.status_code == 200: # 200 OK for successful attachment
            print(f"✅ 라우팅 테이블 '{routing_table_id}'에 인터넷 게이트웨이 '{internet_gateway_id}' 연결 성공! (Region: {region_code})")
            return True
        else:
            print(f"❌ 라우팅 테이블에 인터넷 게이트웨이 연결 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return False
            
    except requests.exceptions.HTTPError as http_err:
        print(f"❗ HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text}")
        return False
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return False

if __name__ == '__main__':
    from get_token import get_token
    # 이 스크립트를 직접 실행할 때 필요한 설정
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]
    
    # 2. 라우팅 테이블 ID (실제 존재하는 라우팅 테이블 ID로 변경해야 합니다)
    example_routing_table_id = "YOUR_ROUTING_TABLE_ID_HERE"
    
    # 3. 인터넷 게이트웨이 ID (실제 존재하는 인터넷 게이트웨이 ID로 변경해야 합니다)
    example_internet_gateway_id = "YOUR_INTERNET_GATEWAY_ID_HERE"

    if auth_token and example_routing_table_id != "YOUR_ROUTING_TABLE_ID_HERE" and example_internet_gateway_id != "YOUR_INTERNET_GATEWAY_ID_HERE":
        attached = attach_gateway_to_routing_table(auth_token, example_routing_table_id, example_internet_gateway_id, "kr1")
        if attached:
            print("✨ 인터넷 게이트웨이 연결 작업 완료.")
        else:
            print("🚨 인터넷 게이트웨이 연결 실패.")
    else:
        print("인증 토큰, 라우팅 테이블 ID 또는 인터넷 게이트웨이 ID를 설정해야 합니다.")