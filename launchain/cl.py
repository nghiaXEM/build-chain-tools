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

# In kiểm tra
print(f"Network ID: {network_id}")
print(f"Server IP: {server_ip}")
print(f"Root Dir: {root_dir}")
print(f"EL HTTP Port: {el_http_port}")
print(f"EL WS Port: {el_ws_port}")
print(f"EL AuthRPC Port: {el_authrpc}")
print(f"EL P2P Port: {el_p2p_port}")
print(f"EL Metrics Port: {el_metrics_port}")

client = docker.from_env()

command = (
    "--accept-terms-of-use=true "
    "--datadir=/data/beacon-data/ "
    f"--execution-endpoint=http://localhost:{el_authrpc} "
    "--rpc-host=0.0.0.0 "
    f"--rpc-port={cl_rpc_port} "
    "--http-host=0.0.0.0 "
    "--http-cors-domain=* "
    f"--http-port={cl_http_port} "
    f"--p2p-host-ip={server_ip} "
    f"--p2p-tcp-port={cl_p2p_tcp_port} "
    f"--p2p-udp-port={cl_p2p_udp_port} "
    f"--p2p-quic-port={cl_p2p_quic_port} "
    "--min-sync-peers=0 "
    "--verbosity=info "
    "--slots-per-archive-point=32 "
    f"--suggested-fee-recipient=0x8943545177806ED17B9F23F0a21ee5948eCaa776 "
    "--jwt-secret=/data/jwt/jwtsecret "
    "--disable-monitoring=false "
    "--monitoring-host=0.0.0.0 "
    f"--monitoring-port={cl_monit_port} "
    "--pprof "
    "--pprofaddr=0.0.0.0 "
    f"--pprofport={cl_pprof_port} "
    "--p2p-static-id=true "
    "--chain-config-file=/data/network-configs/config.yaml "
    "--genesis-state=/data/network-configs/genesis.ssz "
    "--contract-deployment-block=0 "
)

# Nếu có bootstrap node thì nối thêm
if cl_bootstrap_node:
    command += f"--bootstrap-node={cl_bootstrap_node} "

host_path = os.path.abspath(root_dir)

cl_container = client.containers.run(
    image="gcr.io/offchainlabs/prysm/beacon-chain:stable",
    name="cl-container-s",
    command=command,
    volumes={
        host_path: {"bind": "/data", "mode": "rw"},
    },
    network_mode="host",
    detach=True,
    remove=False,
)

#geth_container.wait()
print("✅ Khởi chạy CL thành công.")

