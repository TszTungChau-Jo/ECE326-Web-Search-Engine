from dotenv import load_dotenv
import os, boto3

# Load variables from your .env file into the environment
load_dotenv()

# Create a boto3 session using your AWS credentials
session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)

# Create EC2 client and test connection
ec2 = session.client("ec2")
regions = [r["RegionName"] for r in ec2.describe_regions()["Regions"]]
print("Connected! Example regions:", regions[:3]) # prints the first three regions from that list
