# reboot_instance.py
import boto3
from env_utils import get_env_var, upsert_env_var

AWS_REGION = get_env_var("AWS_REGION")
INSTANCE_ID = get_env_var("ECE326_INSTANCE_ID")

ec2 = boto3.client("ec2", region_name=AWS_REGION)

print(f"Rebooting instance: {INSTANCE_ID}")
ec2.reboot_instances(InstanceIds=[INSTANCE_ID])
print("Reboot request sent. The instance will restart shortly (IP unchanged).")

# Update local .env state
upsert_env_var("ECE326_STATE", "rebooting")
print("Updated ECE326_STATE=rebooting in .env")
