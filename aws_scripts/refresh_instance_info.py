# refresh_instance_info.py
import boto3
from env_utils import get_env_var, upsert_env_var

AWS_REGION = get_env_var("AWS_REGION")
INSTANCE_ID = get_env_var("ECE326_INSTANCE_ID")
ec2 = boto3.client("ec2", region_name=AWS_REGION)

desc = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
inst = desc["Reservations"][0]["Instances"][0]

state = inst["State"]["Name"]
ip = inst.get("PublicIpAddress", "")
dns = inst.get("PublicDnsName", "")

upsert_env_var("ECE326_STATE", state)
upsert_env_var("ECE326_PUBLIC_IP", ip)
upsert_env_var("ECE326_PUBLIC_DNS", dns)

print(f"Updated state={state}, IP={ip}, DNS={dns}")
