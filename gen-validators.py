import docker
import os
import getpass
import shutil

def is_valid_mnemonic(mnemonic):
    return len(mnemonic.strip().split()) == 24

def is_valid_password(pw):
    return len(pw.encode("utf-8")) > 32

def main():
    # --- Nhập mnemonic ---
    while True:
        mnemonic = input("📥 Nhập mnemonic (24 từ cách nhau bằng dấu cách): ").strip()
        if is_valid_mnemonic(mnemonic):
            break
        print("❌ Mnemonic phải có đúng 24 từ. Vui lòng nhập lại.")

    # --- Nhập chỉ số ---
    while True:
        try:
            start = int(input("🔢 Nhập chỉ số bắt đầu (source-min): "))
            end = int(input("🔢 Nhập chỉ số kết thúc (source-max): "))
            if start < end:
                break
            else:
                print("❌ start phải nhỏ hơn end.")
        except ValueError:
            print("❌ Vui lòng nhập số nguyên hợp lệ.")

    # --- Nhập mật khẩu ---
    while True:
        password = getpass.getpass("🔐 Nhập mật khẩu (ít nhất 33 bytes): ")
        if is_valid_password(password):
            break
        print("❌ Mật khẩu phải dài hơn 32 bytes. Vui lòng nhập lại.")

    # Khởi tạo Docker client
    client = docker.from_env()

    # Thư mục mount ra ngoài
    validator_output_path = os.path.abspath("validators")
    os.makedirs(validator_output_path, exist_ok=True)

    # Câu lệnh val-tools
    val_tools_cmd = (
        f"keystores "
        f"--insecure "
        f"--prysm-pass={password} "
        f"--source-min={start} "
        f"--source-max={end} "
        f"--source-mnemonic='{mnemonic}' "
	f"--out-loc=/data/validator-keys"
    )

    print("\n📦 Đang chạy lệnh:")
    print(val_tools_cmd)
    print("⏳ Đang tạo validator keystore...\n")

    # Chạy container
    val_tools_container = client.containers.run(
        image="protolambda/eth2-val-tools:latest",
        name="eth2-vt-container",
        command=val_tools_cmd,
        user=str(os.getuid()),
        volumes={
            validator_output_path: {"bind": "/data", "mode": "rw"},
        },
        remove=False,
        stdin_open=True,
        tty=False,
        detach=True,
    )

    val_tools_container.wait()
    val_tools_container.remove()

    print("✅ Validator keystore đã được tạo tại thư mục `validator-keys/prysm/`.")

    # --- Ghi mật khẩu ra file ---
    prysm_password_dir = os.path.abspath("./validators/prysm-password")
    os.makedirs(prysm_password_dir, exist_ok=True)
    password_path = os.path.join(prysm_password_dir, "prysm-password.txt")
    with open(password_path, "w") as f:
        f.write(password.strip())

    print(f"🔐 Đã lưu mật khẩu tại `{password_path}`.")

if __name__ == "__main__":
    main()
