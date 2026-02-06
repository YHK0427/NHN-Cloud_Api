import requests
import json
from datetime import datetime, timezone
import os
# from dotenv import load_dotenv # 진입점에서 로드하므로 여기서는 필요 없음

# token.json 파일의 경로를 프로젝트 루트 기준으로 지정합니다.
# nhn_api_module/auth.py -> nhn_api_module/ -> nhn_api/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOKEN_FILE = os.path.join(project_root, "token.json")

def save_token(token_data):
    """토큰 데이터를 JSON 파일에 저장합니다."""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=4)

def load_token():
    """
    JSON 파일에서 토큰 데이터를 로드합니다.
    파일이 존재하고 유효한 경우 토큰 데이터를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            return token_data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def parse_datetime(dt_str):
    """
    ISO 형식의 날짜/시간 문자열을 파싱하여 datetime 객체로 변환합니다.
    "Z"로 끝나는 UTC 시간을 처리합니다.
    """
    if dt_str.endswith('Z'):
        dt_str = dt_str[:-1] + '+00:00'
    return datetime.fromisoformat(dt_str)

def get_token():
    """
    NHN Cloud API 인증 토큰을 발급받습니다.

    먼저 `token.json` 파일에 캐시된 유효한 토큰이 있는지 확인합니다.
    유효한 토큰이 없거나 만료된 경우, API를 통해 새 토큰을 발급받고 파일에 캐시합니다.
    
    필요한 환경 변수:
    - TENANT_ID: NHN Cloud 프로젝트의 테넌트 ID
    - API_USERNAME: NHN Cloud API 사용자 이름
    - API_PASSWORD: NHN Cloud API 비밀번호

    Returns:
        성공 시 토큰 정보가 담긴 dict, 실패 시 None
    """
    
    # 기존에 캐시된 토큰이 있는지 확인
    cached_token = load_token()
    if cached_token:
        try:
            expires_at = parse_datetime(cached_token['token_expires'])
            if expires_at > datetime.now(timezone.utc):
                print("유효한 캐시 토큰을 사용합니다.")
                return cached_token
            else:
                print("캐시된 토큰이 만료되었습니다. 새 토큰을 발급합니다.")
        except (KeyError, ValueError) as e:
            print(f"캐시된 토큰 처리 중 오류 발생: {e}. 새 토큰을 발급합니다.")

    print("API로부터 새 토큰을 발급합니다.")
    url = "https://api-identity-infrastructure.nhncloudservice.com"
    uri = "/v2.0/tokens"
    
    # .env 파일에서 민감한 정보 로드
    tenant_id = os.getenv("TENANT_ID")
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")

    if not all([tenant_id, username, password]):
        print("🚨 오류: TENANT_ID, API_USERNAME, API_PASSWORD 환경 변수가 설정되지 않았습니다.")
        print("    .env.example 파일을 .env 파일로 복사한 후, 내용을 올바르게 채워주세요.")
        return None

    body = {
        "auth": {
            "tenantId": tenant_id,
            "passwordCredentials": {
                "username": username,
                "password": password
            }
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url + uri, json=body, headers=headers)
        response.raise_for_status()  # 4xx 또는 5xx 응답 코드인 경우 예외 발생

        token_data = response.json()["access"]["token"]
        
        token_dict = {
            "token_id": token_data["id"],
            'token_expires': token_data["expires"],
            'token_issued_at': token_data["issued_at"]
        }

        save_token(token_dict)
        print("✅ 새 토큰을 발급받아 token.json 파일에 저장했습니다.")
        return token_dict

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 토큰 발급 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 예상치 못한 오류 발생: {e}")
        return None


if __name__ == "__main__":
    # 이 스크립트를 직접 실행할 때의 테스트 로직
    print("인증 모듈 테스트...")
    token = get_token()
    if token:
        print("성공적으로 발급된 토큰 정보:")
        print(json.dumps(token, indent=4))
