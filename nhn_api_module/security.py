# nhn_api_module/security.py

"""
NHN Cloud 보안 그룹 관련 API를 호출하는 함수들을 모아놓은 모듈입니다.
- 보안 그룹
- 보안 그룹 규칙
"""

import requests
import json

def create_security_group(token: str, sg_name: str, description: str = "", region_code: str = "kr1"):
    """
    보안 그룹을 생성합니다.

    :param token: 인증 토큰
    :param sg_name: 생성할 보안 그룹의 이름
    :param description: 보안 그룹에 대한 설명
    :param region_code: 리전 코드
    :return: 성공 시 보안 그룹 ID, 실패 시 None
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/security-groups"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "security_group": {
            "name": sg_name,
            "description": description
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        sg_info = response.json().get('security_group', {})
        print(f"✅ 보안 그룹 '{sg_name}' 생성 성공 (ID: {sg_info.get('id')})")
        return sg_info.get('id')

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 보안 그룹 생성 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 보안 그룹 생성 중 예상치 못한 오류 발생: {e}")
        return None

def create_security_group_rule(
    token: str,
    security_group_id: str,
    direction: str,
    protocol: str = None,
    port_range_min: int = None,
    port_range_max: int = None,
    remote_ip_prefix: str = None,
    description: str = None,
    region_code: str = "kr1"
):
    """
    보안 그룹 규칙을 생성합니다.

    :param token: 인증 토큰
    :param security_group_id: 규칙을 추가할 보안 그룹의 ID
    :param direction: 규칙의 방향 ("ingress" 또는 "egress")
    :param protocol: 프로토콜 (예: "tcp", "udp", "icmp")
    :param port_range_min: 시작 포트 번호
    :param port_range_max: 종료 포트 번호
    :param remote_ip_prefix: 원격 IP 주소 또는 CIDR (예: "0.0.0.0/0")
    :param description: 규칙에 대한 설명
    :param region_code: 리전 코드
    :return: 성공 시 규칙 ID, 실패 시 None
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
    
    payload = {
        "security_group_rule": rule_payload
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        rule_info = response.json().get('security_group_rule', {})
        print(f"✅ 보안 그룹 규칙 생성 성공 (방향: {direction}, 프로토콜: {protocol or 'any'}, 포트: {port_range_min or 'any'}-{port_range_max or 'any'})")
        return rule_info.get('id')

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 보안 그룹 규칙 생성 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 보안 그룹 규칙 생성 중 예상치 못한 오류 발생: {e}")
        return None
