# generate_ssh_helpers.py
import pathlib
from env_utils import get_env_var

def main():
    # Load from .env
    ip = get_env_var("ECE326_PUBLIC_IP")
    pem_name = f"ece326-group{get_env_var('ECE326_GROUP')}-{get_env_var('ECE326_USER').lower()}-key.pem"
    pem_path = (pathlib.Path(__file__).parent / pem_name).resolve()

    print("\n=== SSH / SCP Helper Commands ===\n")

    print("SSH (direct):")
    print(f'  ssh -i "{pem_path}" ubuntu@{ip}\n')

    print("SSH (tunnel for localhost:8080):")
    print(f'  ssh -i "{pem_path}" -L 8080:localhost:8080 ubuntu@{ip}\n')

    print("Check cloud-init logs if needed:")
    print("  sudo tail -n 200 /var/log/cloud-init-output.log\n")

    print("SCP example:")
    print(f'  scp -i "{pem_path}" ./local.txt ubuntu@{ip}:~/remote.txt\n')

    print("=================================\n")

if __name__ == "__main__":
    main()
