# nhn_api_module/networking.py

"""
NHN Cloud 네트워킹 관련 API를 호출하는 함수들을 모아놓은 모듈입니다.
- VPC (가상 프라이빗 클라우드)
- 서브넷
- 인터넷 게이트웨이
- 라우팅 테이블
- Floating IP (공인 IP)
"""

import requests
import json

# --- VPC ---

def create_vpc(token: str, vpc_name: str, cidr: str, region_code: str = "kr1"):
    """
    VPC를 생성합니다.

    :param token: 인증 토큰
    :param vpc_name: 생성할 VPC의 이름
    :param cidr: VPC의 CIDR (예: "10.0.0.0/16")
    :param region_code: 리전 코드 (예: "kr1")
    :return: 성공 시 VPC ID, 실패 시 None
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/vpcs"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "vpc": {
            "name": vpc_name,
            "cidrv4": cidr
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        vpc_info = response.json().get('vpc', {})
        print(f"✅ VPC '{vpc_name}' 생성 성공 (Region: {region_code})")
        print(f" - ID: {vpc_info.get('id')}")
        return vpc_info.get('id')
            
    except requests.exceptions.HTTPError as http_err:
        print(f"❗ VPC 생성 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ VPC 생성 중 예상치 못한 오류 발생: {e}")
        return None

def get_vpc_details(token: str, vpc_id: str, region_code: str = "kr1"):
    """
    특정 VPC의 상세 정보를 조회합니다.

    :param token: 인증 토큰
    :param vpc_id: 조회할 VPC의 ID
    :param region_code: 리전 코드
    :return: 성공 시 VPC 상세 정보 dict, 실패 시 None
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/vpcs/{vpc_id}"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        vpc_details = response.json().get('vpc', {})
        print(f"✅ VPC 상세 정보 조회 성공 (ID: {vpc_id})")
        return vpc_details
            
    except requests.exceptions.HTTPError as http_err:
        print(f"❗ VPC 상세 정보 조회 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ VPC 상세 정보 조회 중 예상치 못한 오류 발생: {e}")
        return None

# --- Subnet ---

def create_vpc_subnet(token: str, vpc_id: str, subnet_name: str, cidr: str, region_code: str = "kr1"):
    """
    VPC 서브넷을 생성합니다.

    :param token: 인증 토큰
    :param vpc_id: 서브넷이 속할 VPC의 ID
    :param subnet_name: 생성할 서브넷의 이름
    :param cidr: 서브넷의 CIDR (예: "10.0.1.0/24")
    :param region_code: 리전 코드
    :return: 성공 시 서브넷 ID, 실패 시 None
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
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        subnet_info = response.json().get('vpcsubnet', {})
        print(f"✅ VPC 서브넷 '{subnet_name}' 생성 성공 (Region: {region_code})")
        print(f" - ID: {subnet_info.get('id')}")
        return subnet_info.get('id')

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 서브넷 생성 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 서브넷 생성 중 예상치 못한 오류 발생: {e}")
        return None

# --- Internet Gateway & Routing ---

def get_external_network_id(token: str, region_code: str = "kr1"):
    """
    외부 연결이 가능한 네트워크(VPC)의 ID를 조회합니다.
    이 ID는 인터넷 게이트웨이 생성 및 Floating IP 할당에 사용됩니다.

    :param token: 인증 토큰
    :param region_code: 리전 코드
    :return: 성공 시 외부 네트워크 ID, 실패 시 None
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/vpcs?router:external=true"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        vpcs_data = response.json().get('vpcs', [])
        external_networks = [vpc for vpc in vpcs_data if vpc.get('router:external') is True]

        if external_networks:
            external_network_id = external_networks[0].get('id')
            print(f"✅ 외부 네트워크 ID 조회 성공: {external_network_id} (Region: {region_code})")
            return external_network_id
        else:
            print("❌ 외부 네트워크를 찾을 수 없습니다.")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 외부 네트워크 조회 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 외부 네트워크 조회 중 예상치 못한 오류 발생: {e}")
        return None

def create_internet_gateway(token: str, ig_name: str, external_network_id: str, region_code: str = "kr1"):
    """
    인터넷 게이트웨이를 생성합니다.

    :param token: 인증 토큰
    :param ig_name: 생성할 인터넷 게이트웨이의 이름
    :param external_network_id: 연결할 외부 네트워크의 ID
    :param region_code: 리전 코드
    :return: 성공 시 인터넷 게이트웨이 ID, 실패 시 None
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
        response.raise_for_status()
        
        ig_info = response.json().get('internetgateway', {})
        print(f"✅ 인터넷 게이트웨이 '{ig_name}' 생성 성공 (ID: {ig_info.get('id')})")
        return ig_info.get('id')
            
    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 인터넷 게이트웨이 생성 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 인터넷 게이트웨이 생성 중 예상치 못한 오류 발생: {e}")
        return None

def attach_gateway_to_routing_table(token: str, routing_table_id: str, internet_gateway_id: str, region_code: str = "kr1"):
    """
    라우팅 테이블에 인터넷 게이트웨이를 연결합니다.

    :param token: 인증 토큰
    :param routing_table_id: 인터넷 게이트웨이를 연결할 라우팅 테이블의 ID
    :param internet_gateway_id: 연결할 인터넷 게이트웨이의 ID
    :param region_code: 리전 코드
    :return: 성공 시 True, 실패 시 False
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
        response.raise_for_status()
        
        print(f"✅ 라우팅 테이블 '{routing_table_id}'에 인터넷 게이트웨이 연결 성공")
        return True
            
    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 라우팅 테이블 게이트웨이 연결 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return False
    except Exception as e:
        print(f"❗ 라우팅 테이블 게이트웨이 연결 중 예상치 못한 오류 발생: {e}")
        return False

# --- Floating IP ---

def create_floating_ip(token: str, floating_network_id: str, region_code: str = "kr1"):
    """
    Floating IP (공인 IP)를 생성(할당)합니다.

    :param token: 인증 토큰
    :param floating_network_id: Floating IP를 할당할 외부 네트워크의 ID
    :param region_code: 리전 코드
    :return: 성공 시 Floating IP 정보(id, ip_address)가 담긴 dict, 실패 시 None
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/floatingips"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "floatingip": {
            "floating_network_id": floating_network_id
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        fip_info = response.json().get('floatingip', {})
        print(f"✅ Floating IP 생성 성공: {fip_info.get('floating_ip_address')}")
        return {
            "id": fip_info.get('id'),
            "ip_address": fip_info.get('floating_ip_address')
        }

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ Floating IP 생성 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ Floating IP 생성 중 예상치 못한 오류 발생: {e}")
        return None

def associate_floating_ip(token: str, floating_ip_id: str, port_id: str, region_code: str = "kr1"):
    """
    Floating IP를 인스턴스의 포트에 연결합니다.

    :param token: 인증 토큰
    :param floating_ip_id: 연결할 Floating IP의 ID
    :param port_id: Floating IP를 연결할 인스턴스 포트의 ID
    :param region_code: 리전 코드
    :return: 성공 시 True, 실패 시 False
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/floatingips/{floating_ip_id}"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "floatingip": {
            "port_id": port_id
        }
    }

    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        print(f"✅ Floating IP '{floating_ip_id}'를 포트 '{port_id}'에 성공적으로 연결했습니다.")
        return True

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ Floating IP 연결 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return False
    except Exception as e:
        print(f"❗ Floating IP 연결 중 예상치 못한 오류 발생: {e}")
        return False
