import requests
import json
from get_token import get_token

def create_security_group_rule(
    token: str,
    security_group_id: str,
    direction: str,  # "ingress" or "egress"
    protocol: str = None, # e.g., "tcp", "udp", "icmp"
    port_range_min: int = None,
    port_range_max: int = None,
    remote_ip_prefix: str = None, # e.g., "0.0.0.0/0" for all IPs, or a specific IP/CIDR
    description: str = None,
    region_code: str = "kr1"
):
    """
    보안 그룹 규칙을 생성하는 함수
    API: POST /v2.0/security-group-rules
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/security-group-rules"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    rule_payload = {
        "security_group_id": security_group_id,
        "direction": direction,
    }
    
    if protocol:
        rule_payload["protocol"] = protocol
    if port_range_min is not None:
        rule_payload["port_range_min"] = port_range_min
    if port_range_max is not None:
        rule_payload["port_range_max"] = port_range_max
    if remote_ip_prefix:
        rule_payload["remote_ip_prefix"] = remote_ip_prefix
    if description:
        rule_payload["description"] = description
    
    # ethertype defaults to IPv4, so no need to explicitly set unless IPv6 is needed later
    # rule_payload["ethertype"] = "IPv4" 

    payload = {
        "security_group_rule": rule_payload
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200 or response.status_code == 201: # Assuming 200 OK for successful creation
            rule_info = response.json().get('security_group_rule', {})
            print(f"✅ 보안 그룹 규칙 생성 성공! (Region: {region_code})")
            print(f" - ID: {rule_info.get('id')}")
            print(f" - 보안 그룹 ID: {rule_info.get('security_group_id')}")
            print(f" - 방향: {rule_info.get('direction')}")
            print(f" - 프로토콜: {rule_info.get('protocol', 'Any')}")
            print(f" - 포트 범위: {rule_info.get('port_range_min', 'Any')}-{rule_info.get('port_range_max', 'Any')}")
            print(f" - 원격 IP 접두사: {rule_info.get('remote_ip_prefix', 'Any')}")
            return rule_info.get('id')
        else:
            print(f"❌ 보안 그룹 규칙 생성 실패 (Status: {response.status_code})")
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

    # 2. 보안 그룹 규칙 생성 시도
    # 실제 보안 그룹 ID와 원하는 규칙으로 변경해야 합니다.
    example_security_group_id = "YOUR_SECURITY_GROUP_ID_HERE"  # 실제 보안 그룹 ID로 변경!
    
    if example_security_group_id == "YOUR_SECURITY_GROUP_ID_HERE":
        print("⚠️ 경고: 'example_security_group_id'를 실제 보안 그룹 ID로 변경해주세요!")
        print("    먼저 create_security_group.py를 실행하여 보안 그룹을 생성하고 ID를 확인하세요.")
    else:
        # HTTP (80번 포트) 허용 규칙 (모든 IP)
        print("--- HTTP (80) 허용 규칙 생성 ---")
        rule_http_id = create_security_group_rule(
            auth_token,
            example_security_group_id,
            direction="ingress",
            protocol="tcp",
            port_range_min=80,
            port_range_max=80,
            remote_ip_prefix="0.0.0.0/0",
            description="Allow HTTP access from anywhere",
            region_code="kr1"
        )
        if rule_http_id:
            print(f"✨ 생성된 HTTP 규칙 ID: {rule_http_id}")

        # SSH (22번 포트) 허용 규칙 (특정 IP 대역)
        print("--- SSH (22) 허용 규칙 생성 (특정 IP 대역) ---")
        rule_ssh_id = create_security_group_rule(
            auth_token,
            example_security_group_id,
            direction="ingress",
            protocol="tcp",
            port_range_min=22,
            port_range_max=22,
            remote_ip_prefix="YOUR_SPECIFIC_IP_CIDR_HERE", # 예: "203.0.113.0/24"
            description="Allow SSH access from specific IP range",
            region_code="kr1"
        )
        if rule_ssh_id:
            print(f"✨ 생성된 SSH 규칙 ID: {rule_ssh_id}")
        else:
            print("⚠️ 경고: SSH 규칙 생성 시 'YOUR_SPECIFIC_IP_CIDR_HERE'를 실제 IP/CIDR로 변경해주세요.")
