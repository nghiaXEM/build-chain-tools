import os
import subprocess
import shutil
import docker

from dotenv import load_dotenv

# Load .env từ file hiện tại hoặc đường dẫn tùy chỉnh
load_dotenv(dotenv_path=".env")  # hoặc ".env" nếu cùng thư mục

# Lấy giá trị từ biến môi trường
network_id = os.getenv("NETWORK_ID")
server_ip = os.getenv("SERVER_IP")
root_dir = os.getenv("ROOT_DIR")

el_http_port = os.getenv("EL_HTTP_PORT")
el_ws_port = os.getenv("EL_WS_PORT")
el_authrpc = os.getenv("EL_AUTHRPC")
el_p2p_port = os.getenv("EL_P2P_PORT")
el_metrics_port = os.getenv("EL_METRICS_PORT")
el_bootnodes = os.getenv("EL_BOOTNODES")

cl_rpc_port = os.getenv("CL_RPC_PORT")
cl_http_port = os.getenv("CL_HTTP_PORT")
cl_p2p_tcp_port = os.getenv("CL_P2P_TCP_PORT")
cl_p2p_udp_port = os.getenv("CL_P2P_UDP_PORT")
cl_p2p_quic_port = os.getenv("CL_P2P_QUIC_PORT")
cl_monit_port = os.getenv("CL_MONIT_PORT")
cl_pprof_port = os.getenv("CL_PPROFPORT")
cl_bootstrap_node = os.getenv("CL_BOOTSTRAP_NODE")

vc_rpc = os.getenv("VC_BEACON_RPC_PROVIDER")
vc_rest = os.getenv("VC_BEACON_REST_API_PROVIDER")
vc_monitor_port = os.getenv("VC_MONIT_PORT")

print(f"VC_BEACON_RPC_PROVIDER = {vc_rpc}")
print(f"VC_BEACON_REST_API_PROVIDER = {vc_rest}")
print(f"VC_MONIT_PORT = {vc_monitor_port}")

client = docker.from_env()

command = (
    f"--accept-terms-of-use=true "
    f"--chain-config-file=/data/network-configs/config.yaml "
    f"--suggested-fee-recipient=0x8943545177806ED17B9F23F0a21ee5948eCaa776 "
    f"--beacon-rpc-provider={vc_rpc} "
    f"--beacon-rest-api-provider={vc_rest} "
    f"--disable-monitoring=false "
    f"--monitoring-host=0.0.0.0 "
    f"--monitoring-port={vc_monitor_port} "
    f"--wallet-dir=/data/validators/validator-keys/prysm "
    f"--wallet-password-file=/data/validators/prysm-password/prysm-password.txt"
)
host_path = os.path.abspath(root_dir)
container_validator = client.containers.run(
    image="gcr.io/prysmaticlabs/prysm/validator:stable",  # hoặc digest cụ thể nếu bạn có
    name="vc-container-s",
    command=command,
    volumes={
      host_path: {"bind": "/data", "mode": "rw"},
    },
    network_mode="host",
    detach=True,
    remove=False,
)
print("✅ Khởi chạy VALIDATOR thành công.")

