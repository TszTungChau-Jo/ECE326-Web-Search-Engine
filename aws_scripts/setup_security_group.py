# setup_security_group.py
"""
ECE326 Lab 2 – Security Group Setup
Combines Step 3 (create_security_group) and Step 4 (authorize_ingress)
"""

import boto3, botocore
from env_utils import get_env_var

# --- Load required environment variables ---
AWS_ACCESS_KEY_ID     = get_env_var("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_var("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = get_env_var("AWS_REGION")
GROUP                 = get_env_var("ECE326_GROUP")

# --- Configuration ---
SG_NAME = f"ece326-group{GROUP}"
SG_DESC = "ECE326 Lab 2 Security Group (ICMP, SSH 22, HTTP 80)"

# --- Connect to AWS EC2 ---
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
ec2 = session.client("ec2")

def ensure_security_group():
    """Create or reuse an ECE326 security group and configure inbound rules."""
    # 1. Check for existing security group
    resp = ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [SG_NAME]}]
    )
    if resp["SecurityGroups"]:
        sg_id = resp["SecurityGroups"][0]["GroupId"]
        print(f"Security group already exists: {SG_NAME} ({sg_id})")
    else:
        # 2. Create new security group in default VPC
        vpc_id = ec2.describe_vpcs()["Vpcs"][0]["VpcId"]
        print(f"Creating security group: {SG_NAME} in {AWS_REGION} (VPC: {vpc_id})")
        sg = ec2.create_security_group(
            GroupName=SG_NAME,
            Description=SG_DESC,
            VpcId=vpc_id,
        )
        sg_id = sg["GroupId"]
        print(f"Created new security group: {SG_NAME} ({sg_id})")

    # 3. Configure ingress rules (idempotent)
    def add_rule(desc, rule):
        try:
            ec2.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=[rule])
            print(f" -> Added {desc}")
        except botocore.exceptions.ClientError as e:
            if "InvalidPermission.Duplicate" in str(e):
                print(f"  (already has {desc})")
            else:
                raise

    print("Setting up ingress rules:")
    add_rule("ICMP (ping)",
        {"IpProtocol": "icmp", "FromPort": -1, "ToPort": -1, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
    )
    add_rule("SSH (port 22)",
        {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
    )
    add_rule("HTTP (port 80)",
        {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
    )

    print("Ingress setup complete.")
    return sg_id

if __name__ == "__main__":
    sg_id = ensure_security_group()
    print(f"Security group ready: {SG_NAME} (ID: {sg_id})")
