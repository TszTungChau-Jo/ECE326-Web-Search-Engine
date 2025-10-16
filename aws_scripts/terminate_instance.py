# terminate_instance.py
import boto3
from env_utils import get_env_var, upsert_env_var

AWS_REGION = get_env_var("AWS_REGION")
INSTANCE_ID = get_env_var("ECE326_INSTANCE_ID")

ec2 = boto3.client("ec2", region_name=AWS_REGION)

print(f"Terminating instance: {INSTANCE_ID}")
ec2.terminate_instances(InstanceIds=[INSTANCE_ID])
print("Instance terminate request sent. It will be permanently deleted.")

# Update local .env state
upsert_env_var("ECE326_STATE", "terminated")
print("Updated ECE326_STATE=terminated in .env")
