# NHN Cloud 리소스 프로비저닝 자동화

## 1. 프로젝트 개요

이 프로젝트는 NHN Cloud에 기본적인 웹 서버 환경을 자동으로 프로비저닝하기 위한 Python 스크립트 모음입니다. 단일 메인 스크립트 실행을 통해 네트워크 인프라(VPC, 서브넷)부터 웹 서버가 구성된 실행 중인 컴퓨팅 인스턴스까지 필요한 모든 클라우드 리소스를 프로그래밍 방식으로 생성합니다.

주요 목표는 NHN Cloud API를 사용하여 인프라를 오케스트레이션하는 방법에 대한 완전한 작동 예제를 제공하는 것입니다.

## 2. 프로젝트의 최종 목표

메인 스크립트(`main.py`)를 실행하면 다음과 같은 완전히 구성된 환경이 생성됩니다:
- 격리된 네트워크를 생성하기 위한 새로운 **VPC** 및 **서브넷**.
- **인터넷 게이트웨이**가 VPC의 라우팅 테이블에 연결되어 외부 네트워크 통신이 가능해집니다.
- **Security Group** with rules to allow **HTTP (port 80)** and **SSH (port 22)** access.
- 지정된 Ubuntu 이미지에서 시작된 새로운 **컴퓨팅 인스턴스** (VM).
- 인스턴스 부팅 시 자동으로 설치 및 시작되는 **Nginx 웹 서버**. (이제 인코딩 문제 없이)
- 인스턴스에 할당 및 연결되어 웹 서버를 인터넷에서 접근 가능하게 하는 **Floating IP** (공인 IP).

성공적으로 완료되면 스크립트는 새로 생성된 웹 서버의 공인 IP 주소를 출력합니다.

## 3. 핵심 기능

- **순차적 오케스트레이션**: `main.py`는 리소스가 올바르게 생성되도록 특정 순서로 다른 모듈을 호출합니다.
- **API 인증**: `get_token.py`는 NHN Cloud Identity 서비스와의 인증을 처리합니다.
- **토큰 캐싱**: 중복된 로그인 요청을 방지하기 위해 인증 토큰은 `token.json` 파일에 캐시되며 만료될 때까지 재사용됩니다.
- **리소스 모듈화**: 각 스크립트는 단일 API 작업(예: `create_vpc.py`, `create_instance.py`)에 중점을 두어 코드를 이해하고 유지 관리하기 쉽게 만듭니다.
- **자동 인스턴스 설정**: 인스턴스는 OS를 자동으로 업데이트하고 Nginx를 설치하는 `user-data` 스크립트를 사용하여 프로비저닝됩니다. (이제 Base64 인코딩을 통해 인코딩 문제 해결)
- **동적 리소스 선택**: 스크립트는 Floating IP 생성을 위한 외부 네트워크를 자동으로 찾고, 기본값이 발견되지 않으면 사용 가능한 가장 작은 인스턴스 플레이버를 선택합니다.
- **자동 인터넷 게이트웨이 설정**: VPC 생성 후 인터넷 게이트웨이를 생성하고 라우팅 테이블에 연결하여 외부 통신이 가능하도록 합니다.

## 4. 프로젝트 구조

```
nhn_api/
├── .gitignore
├── main.py                     # 모든 단계를 실행하는 메인 오케스트레이터 스크립트.
├── config.py                   # 모든 설정 변수를 포함하는 파일 (사용자 설정 필요).
├── get_token.py                # API 인증 및 토큰 캐싱을 처리합니다.
├── create_vpc.py               # 가상 프라이빗 클라우드(VPC)를 생성합니다.
├── get_vpc_details.py          # 특정 VPC의 상세 정보를 조회합니다.
├── create_vpc_subnet.py        # VPC 내에 서브넷을 생성합니다.
├── create_internet_gateway.py  # 인터넷 게이트웨이를 생성합니다.
├── attach_gateway_to_routing_table.py # 라우팅 테이블에 인터넷 게이트웨이를 연결합니다.
├── create_security_group.py    # 보안 그룹을 생성합니다.
├── create_security_group_rule.py # 보안 그룹에 규칙(예: HTTP, SSH용)을 추가합니다.
├── create_instance.py          # 컴퓨팅 인스턴스(VM)를 생성합니다.
├── create_floating_ip.py       # 새로운 Floating (공인) IP를 할당합니다.
├── associate_floating_ip.py    # Floating IP를 인스턴스에 연결합니다.
├── get_external_network_id.py  # Floating IP에 필요한 공용 네트워크의 ID를 찾습니다.
├── list_flavors.py             # 사용 가능한 인스턴스 유형(사양)을 나열합니다.
├── list_key_pairs.py           # 사용 가능한 SSH 키 페어를 나열합니다.
├── get_my_instance.py          # (도우미) 기존 인스턴스의 세부 정보를 가져옵니다.
├── token.json                  # (생성됨) API 인증 토큰을 캐시합니다.
└── venv/                       # Python 가상 환경.
```

## 5. 전제 조건

- Python 3.x
- `requests` 라이브러리. pip를 사용하여 설치하세요:
  ```bash
  pip install requests
  ```

## 6. 구성 (중요!)

프로젝트를 실행하기 전에 다음 파일에서 개인 자격 증명 및 설정을 **반드시** 구성해야 합니다.

### a. `get_token.py` (인증 자격 증명)

`get_token.py`를 열고 `body` 딕셔너리를 NHN Cloud API 자격 증명으로 수정합니다.

```python
# get_token.py 내
def get_token():
    # ...
    tenant_id = "YOUR_TENANT_ID_HERE" # <-- 이 값은 config.py에서 관리되므로 변경하지 마세요.
    body = {
        "auth": {
            "tenantId": tenant_id, # `config.py`에서 임포트됩니다.
            "passwordCredentials": {
                "username": "test04",        # <-- 실제 API 사용자 이름으로 변경하세요
                "password": "test123!@#"      # <-- 실제 API 비밀번호로 변경하세요
            }
        }
    }
    # ...
```

> **⚠️ 보안 경고:** 소스 코드에 자격 증명을 직접 하드코딩하는 것은 심각한 보안 위험입니다. 프로덕션 사용의 경우 환경 변수나 전용 비밀 관리 도구와 같은 더 안전한 방법을 사용하는 것을 강력히 권장합니다.

### b. `config.py` (리소스 구성)

`config.py`를 열고 다음 변수를 NHN Cloud 프로젝트에 맞게 구성합니다.

```python
# config.py 내

# --- Configuration ---
region_code = "kr1" # 리전 코드 (예: "kr1", "jp1" 등)
tenant_id = "YOUR_TENANT_ID_HERE" # <-- 실제 테넌트 ID로 변경하세요

# VPC and Subnet
vpc_name = "my-python-vpc" # 생성할 VPC의 이름
vpc_cidr = "10.0.0.0/16" # VPC의 CIDR
subnet_name = "my-python-subnet" # 생성할 서브넷의 이름
subnet_cidr = "10.0.1.0/24" # 서브넷의 CIDR (VPC CIDR 내에 있어야 합니다)

# Security Group and Rules
sg_name = "my-python-sg" # 생성할 보안 그룹의 이름
sg_description = "Security group for web server and SSH access" # 보안 그룹 설명
my_ip_for_ssh = "1.231.165.73/32" # <-- SSH 접근을 허용하기 위해 자신의 공인 IP 주소와 /32 접미사로 변경하세요.

# Instance Configuration
instance_name = "my-web-instance" # 생성할 인스턴스의 이름
image_ref = "7342b6e2-74d6-4d2c-a65c-90242d1ee218" # <-- 사용할 이미지의 ID (예: Ubuntu Server 24.04.3 LTS)
key_name = "yh_vm" # <-- NHN Cloud 프로젝트에 존재하는 키 페어의 이름으로 변경하세요.
volume_size = 30 # 인스턴스에 할당할 볼륨 크기 (GB)

# Nginx 설치 User Data 스크립트는 필요에 따라 수정하세요.
# (Base64 인코딩을 통해 한글 인코딩 문제 해결)
```

## 7. 실행 방법

구성 단계를 완료한 후 터미널에서 메인 스크립트를 실행합니다:

```bash
python main.py
```

스크립트는 인증부터 Floating IP의 최종 연결까지 각 단계의 진행 상황을 출력합니다.

## 8. 실행 흐름

`main.py` 스크립트는 다음 작업을 순서대로 수행합니다:
1.  **토큰 가져오기**: `get_token.py`를 사용하여 인증 토큰을 가져옵니다.
2.  **VPC 생성**: 새로운 가상 프라이빗 클라우드를 생성합니다.
3.  **서브넷 생성**: 새로 생성된 VPC에 서브넷을 추가합니다.
4.  **VPC 상세 정보 조회 및 라우팅 테이블 ID 찾기**: VPC의 상세 정보를 조회하여 서브넷에 연결된 라우팅 테이블의 ID를 얻습니다.
5.  **외부 네트워크 ID 가져오기**: 인터넷 게이트웨이 및 플로팅 IP에 필요한 외부 네트워크 ID를 가져옵니다.
6.  **인터넷 게이트웨이 생성**: 외부 네트워크에 연결될 인터넷 게이트웨이를 생성합니다.
7.  **인터넷 게이트웨이를 라우팅 테이블에 연결**: 생성된 인터넷 게이트웨이를 VPC의 라우팅 테이블에 연결하여 외부 통신 경로를 설정합니다.
8.  **보안 그룹 생성**: 방화벽 규칙을 포함할 보안 그룹을 생성합니다.
9.  **보안 규칙 추가**: HTTP (80번 포트, 내 IP에서) 및 SSH (22번 포트, 지정된 IP에서)에 대한 인바운드 규칙을 추가합니다.
10. **플레이버 나열**: 사용 가능한 인스턴스 크기 목록을 검색하고 작은 것을 선택합니다.
11. **인스턴스 생성**: 지정된 이미지, 키 페어, 플레이버 및 네트워크 설정으로 새로운 가상 머신을 프로비저닝합니다. 또한 Nginx 설치 스크립트를 삽입합니다.
12. **플로팅 IP 생성**: 사용 가능한 풀에서 공인 IP 주소를 할당합니다.
13. **플로팅 IP 연결**: 새 공인 IP를 인스턴스의 네트워크 포트에 연결합니다.
14. **최종 요약**: 할당된 Floating IP 주소를 출력하여 웹 서버에 접근할 수 있도록 합니다.

## 9. 정리

이 프로젝트에는 자동 리소스 삭제 스크립트가 포함되어 있지 않습니다. 요금이 부과되는 것을 방지하려면 작업 완료 후 **NHN Cloud 콘솔**을 통해 생성된 리소스를 수동으로 삭제해야 합니다. 리소스를 생성 역순으로 삭제하는 것을 기억하세요:
1.  Floating IP (해제)
2.  인스턴스 (종료)
3.  인터넷 게이트웨이 (삭제)
4.  보안 그룹 (삭제)
5.  서브넷 (삭제)
6.  VPC (삭제)