import json
import boto3
from io import BytesIO


def load_flopping_counts(bucket_name, s3_key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=s3_key)
    data = json.loads(response["Body"].read().decode("utf-8"))
    return data


def save_flopping_counts(data, bucket_name, s3_key):
    s3 = boto3.client("s3")
    s3.upload_fileobj(BytesIO(json.dumps(data).encode("utf-8")), bucket_name, s3_key)


def process_data(bucket_name, s3_key):
    # Load the existing data from the S3 bucket
    data = load_flopping_counts(bucket_name, s3_key)

    # Process the data from the API or scraping
    # Update the data in memory

    # Save the updated data back to the S3 bucket
    save_flopping_counts(data, bucket_name, s3_key)


def sort_flopping_counts_descending(filepath, bucket_name, s3_key):
    s3 = boto3.client("s3")

    try:
        # Read existing data from S3
        response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        data = json.loads(response["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        # If the file doesn't exist, initialize with an empty dictionary
        data = {}

    # Sort the data and update the dictionary
    items = list(data.items())
    sorted_items = sorted(
        items,
        key=lambda x: x[1]["count"] if isinstance(x[1], dict) else x[1],
        reverse=True,
    )
    for player, details in sorted_items:
        data[player] = details

    # Upload the updated data to S3
    s3.upload_fileobj(BytesIO(json.dumps(data).encode("utf-8")), bucket_name, s3_key)

    print("Flopping counts sorted and saved to S3 bucket.")


# Usage example
# process_data("your-bucket-name", "flopping_counts.json")


def main():
    process_data("your-bucket-name", "flopping_counts.json")


# lambda handler that runs the main() function
def lambda_handler(event, context):
    main()
