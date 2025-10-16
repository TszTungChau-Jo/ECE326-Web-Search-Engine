# list_instances.py
import boto3
from env_utils import get_env_var

AWS_REGION = get_env_var("AWS_REGION")
ec2 = boto3.resource("ec2", region_name=AWS_REGION)

for i in ec2.instances.all():
    print(f"ID: {i.id}, State: {i.state['Name']}, IP: {i.public_ip_address}, Tags: {i.tags}")
