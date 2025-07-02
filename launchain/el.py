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

geth_command = (
    f"--networkid={network_id} "
    f"--verbosity=3 "
    f"--datadir=/data/gethdata "
    f"--http --http.addr=0.0.0.0 --http.port={el_http_port} --http.vhosts=* --http.corsdomain=* "
    f"--http.api=admin,engine,net,eth,web3,debug,txpool "
    f"--ws --ws.addr=0.0.0.0 --ws.port={el_ws_port} --ws.api=admin,engine,net,eth,web3,debug,txpool "
    f"--ws.origins=* "
    f"--allow-insecure-unlock "
    f"--nat=extip:{server_ip} "
    f"--authrpc.port={el_authrpc} --authrpc.addr=0.0.0.0 --authrpc.vhosts=* --authrpc.jwtsecret=/data/jwt/jwtsecret "
    f"--syncmode=full "
    f"--rpc.allow-unprotected-txs "
    f"--metrics --metrics.addr=0.0.0.0 --metrics.port={el_metrics_port} "
    f"--discovery.port={el_p2p_port} --port={el_p2p_port} "
    f"--miner.gasprice=1"
)

# Thêm dòng bootnodes nếu tồn tại
if el_bootnodes:
    geth_command += f" --bootnodes={el_bootnodes}"

# In kiểm tra (tùy chọn)
print("\n🚀 Lệnh Geth:")
print(geth_command)

host_path = os.path.abspath(root_dir)

geth_container = client.containers.run(
    image="ethereum/client-go:latest",
    name="geth-container-s",
    command=geth_command,
    volumes={
        host_path: {"bind": "/data", "mode": "rw"},
    },
    network_mode="host",
    detach=True,
    remove=False,
)

#geth_container.wait()
print("✅ Khởi chạy GETH thành công.")

