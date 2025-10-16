# create_instance.py — with concise UserData calling your bootstrap.sh
import pathlib
import boto3, botocore
from env_utils import get_env_var, upsert_env_var, write_instance_manifest

# --- Env ---
AWS_ACCESS_KEY_ID     = get_env_var("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_var("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = get_env_var("AWS_REGION")
GROUP                 = get_env_var("ECE326_GROUP")
USER                  = get_env_var("ECE326_USER").lower()
AMI_ID                = get_env_var("ECE326_AMI_ID")          # <- set in .env
INSTANCE_TYPE         = get_env_var("ECE326_INSTANCE_TYPE")   # e.g., t3.micro

SG_NAME  = f"ece326-group{GROUP}"
KEY_NAME = f"ece326-group{GROUP}-{USER}-key"
PEM_PATH = (pathlib.Path(__file__).parent / f"{KEY_NAME}.pem").resolve()

# --- AWS session ---
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
ec2_client = session.client("ec2")
ec2_res    = session.resource("ec2")

def ensure_keypair_exists(name: str):
    try:
        ec2_client.describe_key_pairs(KeyNames=[name])
    except botocore.exceptions.ClientError as e:
        if "InvalidKeyPair.NotFound" in str(e):
            raise RuntimeError(f"Key pair '{name}' not found. Run create_keypair.py first.")
        raise

def get_security_group_id_by_name(name: str) -> str:
    resp = ec2_client.describe_security_groups(Filters=[{"Name": "group-name", "Values": [name]}])
    groups = resp.get("SecurityGroups", [])
    if not groups:
        raise RuntimeError(f"Security group '{name}' not found. Run setup_security_group.py first.")
    return groups[0]["GroupId"]

def main():
    ensure_keypair_exists(KEY_NAME)
    sg_id = get_security_group_id_by_name(SG_NAME)

    print("=== Launch parameters ===")
    print(f"Region:         {AWS_REGION}")
    print(f"AMI:            {AMI_ID}")
    print(f"Instance type:  {INSTANCE_TYPE}")
    print(f"KeyName:        {KEY_NAME}")
    print(f"Security Group: {SG_NAME} ({sg_id})")

    # --- Launch with cloud-init (UserData) that calls the repo's bootstrap.sh ---
    instances = ec2_res.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[sg_id],
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": f"ece326-group{GROUP}-web"},
                {"Key": "Owner", "Value": USER},
                {"Key": "Course", "Value": "ECE326-Lab2"},
            ],
        }],
        UserData="""#!/bin/bash
set -euo pipefail
apt-get update -y && apt-get install -y git
cd /home/ubuntu
# clone once; safe if it already exists
sudo -u ubuntu git clone https://github.com/TszTungChau-Jo/ECE326-Web-Search-Engine.git || true
# run your bootstrap (keeps app on localhost:8080 for SSH tunneling)
chmod +x /home/ubuntu/ECE326-Web-Search-Engine/aws_scripts/bootstrap.sh
sudo -u ubuntu bash /home/ubuntu/ECE326-Web-Search-Engine/aws_scripts/bootstrap.sh
"""
    )

    # Wait until running
    instance = instances[0]
    print(f"Created instance: {instance.id}")
    print("Waiting for 'running' ...")
    instance.wait_until_running()
    instance.reload()

    # Fetch key details
    ip   = instance.public_ip_address
    dns  = instance.public_dns_name
    state= instance.state["Name"]
    
    # Save core info to .env
    upsert_env_var("ECE326_INSTANCE_ID", instance.id)
    upsert_env_var("ECE326_PUBLIC_IP", ip or "")
    upsert_env_var("ECE326_PUBLIC_DNS", dns or "")
    upsert_env_var("ECE326_STATE", state or "")

    # Save richer manifest
    manifest = {
        "instance_id": instance.id,
        "region": AWS_REGION,
        "state": state,
        "public_ip": ip,
        "public_dns": dns,
        "launch_time": getattr(instance, "launch_time", None).isoformat() if getattr(instance, "launch_time", None) else None,
        "tags": instance.tags,
        "key_name": KEY_NAME,
        "security_group": {"name": SG_NAME, "id": sg_id},
        "ami_id": AMI_ID,
        "instance_type": INSTANCE_TYPE,
    }
    write_instance_manifest(manifest)
    print("\nInstance info saved to .env and last_instance.json\n")
    
    # SSH/SCP helpers (Ubuntu AMIs default to user 'ubuntu')
    print("\nSSH (direct):")
    print(f'  ssh -i "{PEM_PATH}" ubuntu@{ip}')

    print("\nSSH (tunnel for localhost:8080):")
    print(f'  ssh -i "{PEM_PATH}" -L 8080:localhost:8080 ubuntu@{ip}')

    print("\nCheck cloud-init logs if needed:")
    print("  sudo tail -n 200 /var/log/cloud-init-output.log")

    print("\nSCP example:")
    print(f'  scp -i "{PEM_PATH}" ./local.txt ubuntu@{ip}:~/remote.txt')


if __name__ == "__main__":
    main()
