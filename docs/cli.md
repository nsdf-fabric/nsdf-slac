# NSDF SLAC CLI

The NSDF SLAC CLI provides a way to access all the processed dark matter data in remote storage. It is composed of a few
commands to enable data access.

## Prerequisites

In order to use the CLI, you will need to setup the credentials. This can be done in two ways.

1. config command: The config command sets up the credentials for you.

2. manually: If you would rather setup the credentials, you will need to specify the profile, and credentials
   as follows:

```bash
# ~/.aws/config
[example-profile]
region = us-east-1
output = json
s3 =
    endpoint_url = https://example-endpoint.com
    signature_version = s3v4
    max_concurrent_requests = 4
```

```bash
# ~/.aws/credentials
[example-profile]
aws_access_key_id = access-key-example
aws_secret_access_key = secret-access-key-example
```

## Local setup

To run locally, you sure to have the following credentials in a `.env` file in the same level as the cli.

```bash
ENDPOINT_URL="your-endpoint-url"
AWS_ACCESS_KEY_ID="your-aws-access-key-id"
AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key"
BUCKET_NAME="your-bucket-name"
```

Then, you can download data as follows

```bash
python cli.py download <mid-file>
```

## Commands

- **version**: The version command provides the semantic versioning of the CLI
- **config**: The config command sets up the credentials to be able to access the processed dark matter data.
- **download**: The download command allows the user to download all the associated processed files related to a mid file.
