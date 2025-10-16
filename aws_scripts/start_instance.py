# start_instance.py
import boto3
from env_utils import get_env_var, upsert_env_var

AWS_REGION = get_env_var("AWS_REGION")
INSTANCE_ID = get_env_var("ECE326_INSTANCE_ID")

ec2 = boto3.client("ec2", region_name=AWS_REGION)

print(f"Starting instance: {INSTANCE_ID}")
ec2.start_instances(InstanceIds=[INSTANCE_ID])
print("Instance start request sent. It may take a few minutes to become running.")

# Update local .env state
upsert_env_var("ECE326_STATE", "pending")
print("Updated ECE326_STATE=pending in .env")
print("Use refresh_instance_info.py later to get updated IP/DNS once running.")
