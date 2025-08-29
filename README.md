# Mini-SOC-Challenge
# SOC Architect - Technical Challenge

This repository is for showcasing the work done by Hamza Moussadeq for the Mini SOC challenge as part of the Cires Technologies interview process for the role of SOC Architect / DevOps Engineer.
## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Docker](#docker)
  - [Python](#python)
  - [Trivy](#trivy)
  - [Chrome/Selenium](#chromeselenium)
  - [Vault](#vault)
- [Deploy Wazuh Locally](#deploy-wazuh-locally)
- [Deploy via CI/CD](#deploy-via-cicd)
- [Security & Secrets](#security-&-secrets)

## Architecture overview

This project implements a DevSecOps pipeline that automates the secure deployment of the Wazuh SIEM stack using GitHub Actions, Docker Compose, Nginx, Trivy, Selenium with chrome driver and HashiCorp Vault.

The architecture integrates:

- GitHub Actions (self-hosted runner) for CI/CD orchestration
- Trivy for vulnerability scanning of Docker images before deployment
- Selenium and Chrome driver for browser based tests
- Docker Compose to deploy the Wazuh Stack:
   - Wazuh Manager
   - Wazuh Indexer
   - Wazuh Dashboard
- Nginx as a reverse proxy in front of the Wazuh Dashboard
- Docker Volumes for persistent Wazuh data
- HashiCorp Vault Server (separate Ubuntu VM) to securely store and retrieve secrets

The project's repository is structured as follows:
```bash
.
├── .github                       
│   └── workflows                 
│       └── test.yml              # GitHub Actions workflow (CI/CD)
├── certs                         # SSL/TLS certificates for secure communication
│   ├── cert.crt                  # Public certificate
│   └── private.key               # Private key for the certificate
│
├── docker                        # Main Docker-based deployment files
│   ├── config                    # Configuration files for Wazuh stack components
│   │   ├── certs.yml             # Certificate configuration for services
│   │   ├── wazuh_cluster
│   │   │   └── wazuh_manager.conf    # Wazuh manager configuration (rules, cluster, etc.)
│   │   ├── wazuh_dashboard
│   │   │   ├── opensearch_dashboards.yml # OpenSearch Dashboards settings
│   │   │   └── wazuh.yml.template       # Wazuh dashboard template configuration
│   │   └── wazuh_indexer
│   │       ├── internal_users.yml       # Local users and roles for OpenSearch
│   │       └── wazuh.indexer.yml        # Wazuh indexer configuration
│   │
│   ├── docker-compose.yml        # Main Docker Compose file to deploy Wazuh stack
│   └── generate-indexer-certs.yml # Utility to generate certificates for the indexer
│
├── nginx                         # Reverse proxy configuration
│   └── nginx.conf             
│
├── README.md                     # Project documentation
│
└── testing                       # Testing and validation scripts
    ├── api_health_check.sh       # Bash script to verify API health
    ├── dashboard_selenium_test.py # Automated test for Wazuh Dashboard (Selenium)
    ├── requirements.txt          # Python dependencies for testing
    └── trivy-reports             # Folder where Trivy vulnerability scan reports are stored


```

## Prerequisites
- A self-hosted runner that the CI/CD pipeline runs on, in order to run the pipeline and the Wazuh stack comfortably, it is recommended to have at least 6gb of ram. Wazuh indexer also creates many memory-mapped areas. So you need to set the kernel to give a process at least 262,144 memory-mapped areas.
1. Increase max_map_count on your Docker host:
```bash
sysctl -w vm.max_map_count=262144
```
2. Update the `vm.max_map_count` setting in `/etc/sysctl.conf` to set this value permanently.

The Runner needs to have these tools installed:
- Docker (along with compose)
- Trivy
- Python3/pip
- Selenium
- Chrome/Chromedriver


- In order to ensure security and avoid the exposure of secrets, a hashicorp vault server can be used , installed on a separate machine, in my case i used a ubuntu 24.04 virtual machine.

## Installation
### Docker
```bash
curl -sSL https://get.docker.com/ | sh
sudo systemctl start docker
```
To check if docker has been installed successfully:
```bash
docker --version
```
you should see something like:
```bash
Docker version 28.3.3, build 980b856
```
Then add your user to the docker group to use docker as a non root user:
```bash
usermod -aG docker <your-user>
```
### Python 3.11
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11
sudo apt install -y python3-pip
sudo apt install python3.12-venv
```
### Trivy
```bash
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```
To make sure Trivy got installed, run:\
```bash
Trivy --version
```
You should see the following: 
```bash
Version: 0.18.3
Vulnerability DB:
  Type: Light
  Version: 1
  UpdatedAt: 2023-02-08 12:48:16.989777838 +0000 UTC
  NextUpdate: 2023-02-08 18:48:16.989777438 +0000 UTC
  DownloadedAt: 2025-08-27 23:10:21.137435118 +0000 UTC
```
### Chrome/Chromedriver + Selenium
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
```
For selenium, it will be installed in a venv, we first need to create it and activate it
```bash
python3 -m venv venv     # create the venv
source venv/bin/activate     # activate it
```
once the virtual environment is activated we can install selenium with pip3:
```bash
pip3 install selenium
```
In order to test if everything is working, we will create a hello_world test file:
- With Chrome Headless (no GUI):
```bash
# nano test.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://python.org")
print(driver.title)
driver.close()
```
- Run it 
```bash
python3 test.py
Welcome to Python.org
```
### Hashicorp Vault 
```bash
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vault
```
We can either use the dev server for simplicity (not recommended for production) and has a drawback of volatility, secrets are not stored permanently. 
1. First, we create a vault-data directory which will hold the data for the vault
```bash
mkdir vault-data
```
2. Create a vault configuration file:
```bash
# nano vault.hcl
vault.hcl
listener "tcp" {
  address     = "0.0.0.0:8200" # make it accessible externally 
  tls_disable = 1     # disable TLS for local testing
}

storage "file" {
  path = "/home/hamza/vault-data"  # folder to store persistent data
}

ui = true  # enable web UI

```
3. Start the vault server
```bash
vault server -config=<path/to/vault-data>
```
4. In another terminal, run:
```bash
export VAULT_ADDR="http://127.0.0.1:8200"
```
5. Initialize the vault:
```bash
vault operator init
```
The unseal keys will be displayed along with the initial root token, you need to save them .When first launched or after a restart, the vault will be sealed. In order to unseal it we need to provide at least 3 unseal keys:
```bash
vault operator unseal <1st-unseal-key>
vault operator unseal <2nd-unseal-key>
vault operator unseal <3rd-unseal-key>
```
After each unseal, the unseal progress will increase until the "Sealed" value becomes false.
6. Login
```bash
vault login <root_token>
```
7. Start putting secrets
```bash
vault kv put secret/mytest password="123456" 
```
Explanation:
- We are using the kv engine which is a key/value, in our example password is the key and 123456 is the value
- `put` so we can create a secret, in order to retrieve it use `get`
- `secret/mytest`is the path of the secret, `mytest` is the secret and `password` is a field
This might not work first because the kv engine might not be enabled yet, in order to enable it run:
```bash
vault secrets enable -path=secret kv
```
To access the vault UI, in your browser type `http://127.0.0.1:8200` (if locally) or with the host IP address (if externally)
## Deploy Wazuh locally
To deploy Wazuh with docker compose, the official Wazuh website offers a ready docker-compose.yml file that we can use 
1. Clone the Wazuh repository to your system:
```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.11.2
```
2. For single node deployment which is the case, cd into the single-node directory
3. Change the default passwords for the indexer users and API users for better security
- For Indexer users which are `admin` and `kibanaserver`, the first step is to generate the hashes of the new passwords:
```bash
docker run --rm -ti wazuh/wazuh-indexer:4.11.2 bash /usr/share/wazuh-indexer/plugins/opensearch-security/tools/hash.sh
# Once prompted, input the new password
``` 
  - Copy the generated hashes and paste them in their respective fields inside `config/wazuh_indexer/internal_users.yml` file
```bash
# internal_users.yml
...
admin:
  hash: "<paste-here>"
  reserved: true
  backend_roles:
  - "admin"
  description: "Demo admin user"
...
kibanaserver:
  hash: "<paste-here>"
  reserved: true
  description: "Demo kibanaserver user"
...
```
  - Open the docker-compose.yml file. Change all occurrences of the old password with the new one.
- For API user wazuh-wui: 
  - Open the file config/wazuh_dashboard/wazuh.yml and modify the value of password parameter.
```bash
...
hosts:
  - 1513629884013:
      url: "https://wazuh.manager"
      port: 55000
      username: wazuh-wui
      password: "<password-here>"
      run_as: false
...
```
  - Open the docker-compose.yml file. Change all occurrences of the old password with the new one.
4. Execute the following command to generate the certificates needed:
```bash
docker compose -f generate-indexer-certs.yml run --rm generator
```
5. To add more security, it is advisable to put the dashboard behind a reverse proxy such as nginx with SSL for Secure HTTPS access to the Wazuh Dashboard
  - First step is to create the certificates for nginx (see ./certs)
  - Create Nginx configuration file:
```bash
# nginx.conf
worker_processes auto;

events {
    worker_connections 1024;
}

http {

    # Main HTTPS server
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate     /etc/ssl/certs/cert.crt;
        ssl_certificate_key /etc/ssl/certs/private.key;

        location / {
            proxy_pass https://wazuh.dashboard:5601;
            proxy_ssl_verify off;            # disable verification because of self-signed certificates
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $remote_addr;
        }
    }
}
```
  - By default, the Wazuh Dashboard Docker container maps port 5601 to the host's port 443 (443:5601). However, when deploying an Nginx reverse proxy to handle HTTPS traffic on port 443, it's essential to ensure that no other services, including Docker containers, are bound to that port.
To avoid conflicts and allow Nginx to exclusively use port 443, update the Wazuh Dashboard container's port mapping to 5601:5601. This change ensures that the dashboard remains accessible on port 5601 while freeing port 443 for secure reverse proxy operations via Nginx. Make these changes to the docker-compose.yml file in wazuh.dashboard servive.
```bash
...
  wazuh.dashboard:
    image: wazuh/wazuh-dashboard:4.12.0
    hostname: wazuh.dashboard
    restart: always
    ports:
      - 5601:5601   # here change it from 443:5601 to 5601:5601
...
```
6. Start the Wazuh single-node deployment using docker-compose:
```bash
docker compose up -d
```
7. The wazuh dashboard will be accessible via `https://<HOST-IP>`. If not changed, the default username and password for the Wazuh dashboard are `admin` and `SecretPassword`
## Wazuh deployment via CI/CD
To deploy Wazuh securely to docker, a github actions workflow has been implemented (see .github/workflows/test.yml). This is what it does:
```bash
                          +----------------------------------+
                          |  GitHub Actions (Self-Hosted)    |
                          +----------------------------------+
                                        |
                                        v
                          +-------------------------------+
                          |   Retrieve secrets from Vault |
                          +-------------------------------+
                                        |
                                        v
                          +-------------------------------+
                          |       Build Docker images     |
                          +-------------------------------+
                                        |
                                        v
                          +-------------------------------+
                          |   Run Trivy scan on images    |
                          +-------------------------------+
                                        |
                        +-----------------------------------+
                        |   High/Critical vulnerabilities?  |
                        +-----------------------------------+
                           | Yes                          | No
                           v                              v
                +------------------+            +-----------------------------+
                |   Pipeline FAIL  |            | Deploy Wazuh stack (testing)|
                +------------------+            +-----------------------------+
                                                            |
                                                            v
                                                +-------------------------------+
                                                |   API Healthcheck tests       |
                                                +-------------------------------+
                                                            |
                                                            v
                                                +-------------------------------+
                                                |  Selenium UI tests (Dashboard)|
                                                +-------------------------------+
                                                            |
                                                            v
                                                +-------------------------------+
                                                |     Deployment SUCCESS ✅     | 
                                                +-------------------------------+


```
For more details on each step of the pipeline refer to the workflow file.

Upon reading the pipeline, it is clear that even though the trivy scan finds high/critical vulnerablities the pipeline will not fail and that is because it will always find them and that will cause the pipeline to never pass. To make it fail simply change the exit code from 0 to 1 like this:
```bash
trivy image --exit-code 0 --severity HIGH,CRITICAL -o $REPORT_FILE $IMAGE # no fail
trivy image --exit-code 1 --severity HIGH,CRITICAL -o $REPORT_FILE $IMAGE # fail on high/critical
```
## Security & Secrets
In this project, no secrets are hardcoded in the repository or in plain YAML files. All sensitive information, including Wazuh credentials, and API keys, is securely stored and managed via HashiCorp Vault on a separate Ubuntu VM. The GitHub Actions workflow retrieves secrets dynamically from Vault at runtime, ensuring that sensitive data is never exposed in the CI/CD pipeline or in Docker configuration files.
