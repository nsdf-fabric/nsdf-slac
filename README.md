# nsdf-slac

- 6.4T bytes 
- 39524 objects

## Access data with rclone

install rclone:

```bash
sudo apt install -y rclone
```

Add this section to your `~/.config/rclone/rclone.conf`:

```ini
[slac_public]
type = s3
env_auth = false
access_key_id = any
secret_access_key = any
endpoint=https://maritime.sealstorage.io/api/v0/s3
```

Access the data

```bash

# list files
rclone ls slac_public:utah/supercdms-data/CDMS/UMN

# copy file
rclone copy slac_public:utah/supercdms-data/CDMS/UMN/R68/Raw/07180811_2320/07180811_2320_F0008.mid.gz .
```

## Access data with awscli

install awscli:

```bash
sudo apt  install -y awscli

python3 -m pip install awscli_plugin_endpoint
```

Add this to your `~/.aws/config` file:

```ini
[profile slac_public]
output = json
s3 =
    endpoint_url = https://maritime.sealstorage.io/api/v0/s3
    signature_version = s3v4
    max_concurrent_requests = 48
```

Add this to your `~/.aws/credentials` file:


```ini
[slac_public]
aws_access_key_id = any
aws_secret_access_key = any
```

Access the data:

```bash

alias s3='aws s3 --profile slac_public --endpoint-url https://maritime.sealstorage.io/api/v0/s3 --no-verify-ssl'

# list files
s3 ls s3://utah/supercdms-data/CDMS/UMN/

# copy files
s3 cp s3://utah/supercdms-data/CDMS/UMN/R68/Raw/07180811_2320/07180811_2320_F0008.mid.gz .
```


## Access data with s5cmd

install s5cmd

```bash
curl -L https://github.com/peak/s5cmd/releases/download/v2.2.2/s5cmd_2.2.2_Linux-64bit.tar.gz | sudo tar xz -C /usr/bin
```

Add this to your `~/.aws/config` file:

```ini
[profile slac_public]
output = json
s3 =
    endpoint_url = https://maritime.sealstorage.io/api/v0/s3
    signature_version = s3v4
    max_concurrent_requests = 48
```

Add this to your `~/.aws/credentials` file:


```ini
[slac_public]
aws_access_key_id = any
aws_secret_access_key = any
```

Access the data:

```bash

alias s5='s5cmd --profile slac_public  --endpoint-url https://maritime.sealstorage.io/api/v0/s3 --no-verify-ssl'

# list files
s5 ls s3://utah/supercdms-data/CDMS/UMN/

# copy files
s5 cp s3://utah/supercdms-data/CDMS/UMN/R68/Raw/07180811_2320/07180811_2320_F0008.mid.gz .
```


## Access data with python/boto3

Install boto3

```bash
python3 -m pip install --upgrade boto3
```

Create a `test_slac.py` file with the following content:

```python

import boto3
from botocore.client import Config

config = Config(signature_version = 's3v4')

s3 = boto3.resource('s3',
  endpoint_url='https://maritime.sealstorage.io/api/v0/s3',
  aws_access_key_id='any',
  aws_secret_access_key='any',
  config=config,
)

bucket = s3.Bucket("utah")

# change this as needed
key="supercdms-data/CDMS/UMN/R68/Raw/07180811_2320/07180811_2320_F0008.mid.gz"
bucket.download_file(key,"example.mid.gz")
print(f"file {key} downloaded")
```


Execute it:

```bash
python3 test-test_slac.py
```

If you just want to access the head of the object:

```python
import boto3
from botocore.client import Config

config = Config(signature_version = 's3v4')
from pprint import pprint

# boto3.set_stream_logger(name='botocore')

s3 = boto3.client('s3',
    endpoint_url='https://maritime.sealstorage.io/api/v0/s3',
    aws_access_key_id='any',
    aws_secret_access_key='any',
    config=config
)

# change this as needed
h=s3.head_object(Bucket="utah",Key="supercdms-data/CDMS/UMN/R68/Raw/07180811_2320/07180811_2320_F0001.mid.gz")

pprint(h)
```
It will print out:

```
{'AcceptRanges': 'bytes',
 'ContentDisposition': 'inline; filename="07180811_2320_F0001.mid.gz"',
 'ContentLength': 51324722,
 'ContentType': 'application/gzip',
 'ETag': '"da19bcf1d26252830e3c77ecb53cf697"',
 'LastModified': datetime.datetime(2024, 2, 20, 17, 52, 36, tzinfo=tzutc()),
 'Metadata': {'Mtime': '1534047716.951417509'},
 'ResponseMetadata': {'HTTPHeaders': {'accept-ranges': 'bytes',
                                      'access-control-expose-headers': 'Content-Disposition',
                                      'content-disposition': 'inline; '
                                                             'filename="07180811_2320_F0001.mid.gz"',
                                      'content-length': '51324722',
                                      'content-type': 'application/gzip',
                                      'date': 'Fri, 23 Feb 2024 01:25:38 GMT',
                                      'etag': '"da19bcf1d26252830e3c77ecb53cf697"',
                                      'last-modified': 'Tue, 20 Feb 2024 '
                                                       '17:52:36 GMT',
                                      'x-amz-meta-mtime': '1534047716.951417509'},
                      'HTTPStatusCode': 200,
                      'RetryAttempts': 0}}
```

## (INTERNAL USE ONLY) Transfer Data 

You need credentials to SLAC data  from `nsdf-vault`


```bash

# this is the prefix
PREFIX=supercdms-data/CDMS/UMN

# rclone 
rclone ls slac_private:${PREFIX}/

# aws
aws s3 --profile slac_private ls s3://${PREFIX}/

# s5cmd
s5cmd --endpoint-url=https://ncsa.osn.xsede.org --profile slac_private --numworkers 64 ls  "s3://${PREFIX}/*"
s5cmd --endpoint-url=https://ncsa.osn.xsede.org --profile slac_private --numworkers 64 du  --humanize "s3://${PREFIX}/*"
```

To sync data between different endpoints, I need to use rclone
- See https://towardsdatascience.com/managing-your-cloud-based-data-storage-with-rclone-32fff991e0b3

```bash
# better to use a screen session
screen -S nsdf-slac-data-transfer

while [[ 1 == 1 ]] ; do
  rclone --progress  --transfers 16  --size-only sync  slac_private://${PREFIX} slac_public://utah/${PREFIX}
done
```
