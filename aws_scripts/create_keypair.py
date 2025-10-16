from dotenv import load_dotenv
import os, stat, pathlib, boto3, botocore
from env_utils import get_env_var

# --- Load all required variables ---
AWS_ACCESS_KEY_ID     = get_env_var("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_var("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = get_env_var("AWS_REGION")
GROUP                 = get_env_var("ECE326_GROUP")
USER                  = get_env_var("ECE326_USER").lower()

# --- Config ---
KEY_NAME = f"ece326-group{GROUP}-{USER}-key"
PEM_PATH = (pathlib.Path(__file__).parent / f"{KEY_NAME}.pem").resolve()

# --- AWS session ---
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
ec2 = session.client("ec2")

def main():
    try:
        # Check if the key pair already exists in AWS
        ec2.describe_key_pairs(KeyNames=[KEY_NAME])
        print(f"Key pair already exists in AWS: {KEY_NAME}")
        print("If you lost the local .pem: delete the key pair in AWS, then rerun this script.")
        return
    except botocore.exceptions.ClientError as e:
        if "InvalidKeyPair.NotFound" not in str(e):
            raise
    
    # Create the key pair
    print(f"Creating key pair: {KEY_NAME} in region {AWS_REGION}")
    kp = ec2.create_key_pair(KeyName=KEY_NAME)
    PEM_PATH.write_text(kp["KeyMaterial"], encoding="utf-8")

    # Try setting the .pem permissions to read-only for the user (0400)
    try:
        os.chmod(PEM_PATH, stat.S_IRUSR)
    except Exception as e:
        print(f"(Note) Could not set 0400 permissions automatically: {e}")

    print(f"Saved private key to: {PEM_PATH}")
    print("Do NOT commit this file. Keep it safe. If lost, delete the key pair in AWS and re-create.")

if __name__ == "__main__":
    main()
