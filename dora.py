import docker
import os
import ipaddress
import socket
import time

client = docker.from_env()

#---------------------------DORA--------------------------------
dora_command = (
    "-config=/config/dora-config.yaml"
)
container_dora = client.containers.run(
    image="ethpandaops/dora:latest",
    name="dora-container",
    command=dora_command,
    volumes={
        os.path.abspath("config/dora-config.yaml"): {"bind": "/config/dora-config.yaml", "mode": "ro"},
    },
    network_mode="host",
    detach=True,
    remove=False,
)

print("✅ Khởi chạy DORA thành công.")
