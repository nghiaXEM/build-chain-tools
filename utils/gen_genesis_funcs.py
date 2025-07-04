import os
import subprocess
import shutil
import docker

client = docker.from_env()

def run_genesis_generator(PWD):
    os.makedirs(os.path.join(PWD, "data"), exist_ok=True)

    docker_cmd = [
        "docker", "run", "--rm", "-it",
        "-u", str(os.getuid()),
        "-v", f"{os.path.join(PWD,'data')}:/data",
        "-v", f"{os.path.join(PWD, 'config')}:/config",
        "ethpandaops/ethereum-genesis-generator:master",
        "all"
    ]

    print("🚀 Đang chạy Docker để tạo genesis...")
    result = subprocess.run(docker_cmd)
    if result.returncode != 0:
        print("❌ Lỗi khi chạy Docker.")
        exit(1)

    print("✅ Genesis tạo thành công!")

def rename_metadata_folder(PWD):
    src = os.path.join(PWD, "data/metadata")
    dst = os.path.join(PWD, "data/network-configs")

    if os.path.exists(dst):
        print("⚠️ Thư mục 'network-configs' đã tồn tại, đang xóa...")
        shutil.rmtree(dst)

    if os.path.exists(src):
        print("🔁 Đổi tên 'metadata' → 'network-configs'")
        shutil.move(src, dst)
    else:
        print("❌ Không tìm thấy thư mục 'metadata' để đổi tên.")
        exit(1)

def move_parsed_to_networkconfigs(PWD):
    current_dir = os.path.join(PWD, "data")
    parsed_path = os.path.join(current_dir, "parsed")
    target_path = os.path.join(current_dir, "network-configs")

    if not os.path.exists(parsed_path):
        print("❌ Không tìm thấy thư mục 'parsed'.")
        return

    if not os.path.exists(target_path):
        print("❌ Thư mục 'network-configs' chưa được tạo.")
        return

    dest = os.path.join(target_path, "parsed")
    if os.path.exists(dest):
        print("⚠️ Thư mục 'parsed' đã tồn tại trong 'network-configs', đang xóa...")
        shutil.rmtree(dest)

    print("🔁 Di chuyển 'parsed' vào 'network-configs'...")
    shutil.move(parsed_path, dest)
    print("✅ Di chuyển thành công.")

def remove_input_and_change_json(PWD):
    for filename in ["change.json", "input.json"]:
        path = os.path.join(PWD, "data", filename)
        if os.path.exists(path):
            print(f"🗑️ Xóa file {filename}...")
            os.remove(path)

def create_share_network_configs(PWD):
    cur_path = os.path.join(PWD, "data")
    src_dir = os.path.join(cur_path, "network-configs")
    dst_dir = os.path.join(cur_path, "share_network_configs")

    # Tạo thư mục đích nếu chưa có
    os.makedirs(dst_dir, exist_ok=True)

    # Danh sách file cần copy
    files_to_copy = ["genesis.json", "genesis.ssz", "config.yaml"]

    for filename in files_to_copy:
        src_file = os.path.join(src_dir, filename)
        dst_file = os.path.join(dst_dir, filename)

        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"✅ Đã copy {filename} → share_network_configs")
        else:
            print(f"⚠️ File không tồn tại: {src_file}")

def create_gethdata(PWD):

    # Đường dẫn tuyệt đối trên host
    network_configs_path = os.path.join(PWD, "data/network-configs")
    output_data_path = os.path.join(PWD, "data/gethdata")

    # Tạo thư mục dữ liệu nếu chưa có
    os.makedirs(output_data_path, exist_ok=True)

    # Geth command
    geth_init_cmd = (
        "init --datadir=/data/gethdata "
        "/network-configs/genesis.json"
    )

    # Chạy container
    print("🚀 Đang khởi tạo Geth với genesis.json...")
    container = client.containers.run(
        image="ethereum/client-go:latest",
        name="geth-init-container",
        command=geth_init_cmd,
        volumes={
            network_configs_path: {"bind": "/network-configs", "mode": "ro"},
            output_data_path: {"bind": "/data/gethdata", "mode": "rw"},
        },
        user=f"{os.getuid()}:{os.getgid()}",
        remove=True,
        detach=False,
    )

    print("✅ Geth init hoàn tất. Dữ liệu đã được mount ra thư mục gethdata.")

def gen_genesis(PWD):
    run_genesis_generator(os.path.abspath("."))
    rename_metadata_folder(PWD)
    move_parsed_to_networkconfigs(PWD)
    remove_input_and_change_json(PWD)
    create_gethdata(PWD)
    create_share_network_configs(PWD)