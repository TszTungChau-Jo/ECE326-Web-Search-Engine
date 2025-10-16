# stop_instance.py
import boto3
from env_utils import get_env_var, upsert_env_var

AWS_REGION = get_env_var("AWS_REGION")
INSTANCE_ID = get_env_var("ECE326_INSTANCE_ID")

ec2 = boto3.client("ec2", region_name=AWS_REGION)

print(f"Stopping instance: {INSTANCE_ID}")
ec2.stop_instances(InstanceIds=[INSTANCE_ID])
print("Instance stop request sent. It may take a few minutes to fully stop.")

# Update local .env state
upsert_env_var("ECE326_STATE", "stopping")
print("Updated ECE326_STATE=stopping in .env")
