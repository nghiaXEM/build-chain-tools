import os
import subprocess
import shutil
import docker

from dotenv import load_dotenv

# Load .env từ file hiện tại hoặc đường dẫn tùy chỉnh
PWD = os.getcwd()
dotenv_path = os.path.join(PWD, ".env")
host_path = os.path.join(PWD, "data")
load_dotenv(dotenv_path=dotenv_path)

client = docker.from_env()

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
vc_suggested_fee_recipient = os.getenv("VC_SUGGESTED_FEE_RECIPIENT")

def run_execution():
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
        f"--gcmode=archive "
        f"--rpc.allow-unprotected-txs "
        f"--metrics --metrics.addr=0.0.0.0 --metrics.port={el_metrics_port} "
        f"--discovery.port={el_p2p_port} --port={el_p2p_port} "
        f"--miner.gasprice=1"
    )

    # Thêm dòng bootnodes nếu tồn tại
    if el_bootnodes:
        geth_command += f" --bootnodes={el_bootnodes}"

    geth_container = client.containers.run(
        image="ethereum/client-go:latest",
        name="geth-container",
        command=geth_command,
        user=f"{os.getuid()}:{os.getgid()}",
        volumes={
            host_path: {"bind": "/data", "mode": "rw"},
        },
        network_mode="host",
        detach=True,
        remove=False,
    )

    # Log theo thời gian thực
    print("📺 Streaming logs từ container...")

    try:
        for line in geth_container.logs(stream=True):
            decoded_line = line.decode().strip()
            print(decoded_line)

            if "Started P2P networking" in decoded_line:
                with open( os.path.join(PWD, "data", "el_ern.txt"), "w") as f:
                    f.write(decoded_line)

            # 👉 Ví dụ: Bắt sự kiện cụ thể trong logs
            if "Started log indexer" in decoded_line:
                break

    except Exception as e:
        print(f"❌ Lỗi khi đọc log Geth: {e}")

    #geth_container.wait()
    print("✅ Khởi chạy GETH thành công.")

def run_consensus():
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
        f"--suggested-fee-recipient={vc_suggested_fee_recipient} "
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

    if cl_bootstrap_node:
        command += f"--bootstrap-node={cl_bootstrap_node} "

    cl_container = client.containers.run(
        image="gcr.io/offchainlabs/prysm/beacon-chain:stable",
        name="cl-container",
        command=command,
        volumes={
            host_path: {"bind": "/data", "mode": "rw"},
        },
        network_mode="host",
        detach=True,
        remove=False,
    )
    try:
        for line in cl_container.logs(stream=True):
            decoded_line = line.decode().strip()
            print(decoded_line)

            # if "Started P2P networking" in decoded_line:
            #     with open( os.path.join(PWD, "data", "el_ern.txt"), "w") as f:
            #         f.write(decoded_line)

            # 👉 Ví dụ: Bắt sự kiện cụ thể trong logs
            if "Connected to new endpoint" in decoded_line:
                break

    except Exception as e:
        print(f"❌ Lỗi khi đọc log Geth: {e}")

    #geth_container.wait()
    print("✅ Khởi chạy Consensus thành công.")

def run_validators():
    command = (
        f"--accept-terms-of-use=true "
        f"--chain-config-file=/data/network-configs/config.yaml "
        f"--suggested-fee-recipient={vc_suggested_fee_recipient} "
        f"--beacon-rpc-provider={vc_rpc} "
        f"--beacon-rest-api-provider={vc_rest} "
        f"--disable-monitoring=false "
        f"--monitoring-host=0.0.0.0 "
        f"--monitoring-port={vc_monitor_port} "
        f"--wallet-dir=/data/validators/validator-keys/prysm "
        f"--wallet-password-file=/data/validators/prysm-password/prysm-password.txt"
    )

    container_validator = client.containers.run(
        image="gcr.io/prysmaticlabs/prysm/validator:stable",  # hoặc digest cụ thể nếu bạn có
        name="vc-container",
        command=command,
        volumes={
        host_path: {"bind": "/data", "mode": "rw"},
        },
        network_mode="host",
        detach=True,
        remove=False,
    )


if __name__ == "__main__":

    #run execution
    run_execution()

    #run consensus
    run_consensus()

    #run validators
    run_validators()
