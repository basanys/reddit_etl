from ast import parse
from curses import A_HORIZONTAL
import boto3
import sys
import configparser
import pathlib


parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
parser.read(f"{script_path}/configuration.conf")

BUCKET_NAME = parser.get("aws_config", "bucket_name")
AWS_KEY = parser.get("aws_config", "aws_access_key_id")
AWS_SECRET = parser.get("aws_config", "aws_secret_access_key")



output_name = sys.argv[1]
FILE_NAME = output_name + ".csv"

s3 = boto3.resource("s3", aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET)
s3.meta.client.upload_file(
    Filename = f"/tmp/{FILE_NAME}",
    Bucket = BUCKET_NAME,
    Key = FILE_NAME
)