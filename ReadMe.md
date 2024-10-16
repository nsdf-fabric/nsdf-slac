# nsdf-slac public data

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

Access the data:

- note: If you get any SSL certificate problem pkease add `--no-check-certificate` to the rclone commands as a temporary workaround

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

s5 du  --humanize "s3://utah/supercdms-data/*"
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
s3 = boto3.resource('s3',endpoint_url='https://maritime.sealstorage.io/api/v0/s3', aws_access_key_id='any', aws_secret_access_key='any', config=config, verify=False,)
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

## (INTERNAL USE ONLY) Convert data

```bash
screen -S nsdf-transfer
source .venv\bin\activate

alias s5='s5cmd --profile slac_public  --endpoint-url https://maritime.sealstorage.io/api/v0/s3 --no-verify-ssl'

python3 convert.py

files=$(find /mnt/hdd2/supercdms-data/ -iname "*.json" | head -n 40)
for it in ${files} ; do
  grep "header" ${it} | wc -l
  # grep data.npz ${it} | wc -l
done


s5 ls --humanize "s3://utah/supercdms-data/CDMS/UMN/R68/Raw/07180808_1558/*.mid.gz"

# 2024/02/27 23:05:43             46.0M  07180808_1558_F0001.mid.gz
# 2024/02/27 23:06:03            176.9M  07180808_1558_F0002.mid.gz
# 2024/02/27 23:06:01            171.9M  07180808_1558_F0003.mid.gz
# 2024/02/27 23:06:03            171.5M  07180808_1558_F0004.mid.gz
# 2024/02/27 23:06:02            173.8M  07180808_1558_F0005.mid.gz
# 2024/02/27 23:06:03            171.4M  07180808_1558_F0006.mid.gz
# 2024/02/27 23:05:49            175.4M  07180808_1558_F0007.mid.gz
# 2024/02/27 23:05:54            172.7M  07180808_1558_F0008.mid.gz
# 2024/02/27 23:06:04            172.7M  07180808_1558_F0009.mid.gz
# 2024/02/27 23:06:03            142.9M  07180808_1558_F0010.mid.gz

s5 ls --humanize "s3://utah/supercdms-data/CDMS/UMN/R68/Raw/07180808_1558/*.mid.gz"

# 2024/02/27 23:05:43             46.0M  07180808_1558_F0001.mid.gz -> 59.2M
# 2024/02/27 23:06:03            176.9M  07180808_1558_F0002.mid.gz -> 215M
# 2024/02/27 23:06:01            171.9M  07180808_1558_F0003.mid.gz -> 209M
# 2024/02/27 23:06:03            171.5M  07180808_1558_F0004.mid.gz
# 2024/02/27 23:06:02            173.8M  07180808_1558_F0005.mid.gz
# 2024/02/27 23:06:03            171.4M  07180808_1558_F0006.mid.gz
# 2024/02/27 23:05:49            175.4M  07180808_1558_F0007.mid.gz
# 2024/02/27 23:05:54            172.7M  07180808_1558_F0008.mid.gz
# 2024/02/27 23:06:04            172.7M  07180808_1558_F0009.mid.gz
# 2024/02/27 23:06:03            142.9M  07180808_1558_F0010.mid.gz

s5 du --humanize "s3://utah/supercdms-data/CDMS/UMN/R68/Raw/07180808_1558/07180808_1558_F0001/*"



```


## (INTERNAL USE ONLY) Transfer Data to the Public

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

# you can use rclone...
while [[ 1 == 1 ]] ; do
  rclone --progress  --transfers 16  --size-only sync  slac_private://${PREFIX} slac_public://utah/${PREFIX}
done

# or see transfer.py which add a checksum
# ...

```




# Install cvmfs


```bash
# https://cvmfs.readthedocs.io/en/stable/cpt-quickstart.html
wget https://ecsft.cern.ch/dist/cvmfs/cvmfs-release/cvmfs-release-latest_all.deb
sudo dpkg -i cvmfs-release-latest_all.deb
rm -f cvmfs-release-latest_all.deb
sudo apt-get update
sudo apt-get install cvmfs

# for windows WSL2
# ln -s /usr/kill /usr/bin/kill
# sudo cvmfs_config wsl2_start

sudo cvmfs_config setup

REPOS="
ams.cern.ch
annie.opensciencegrid.org
argoneut.opensciencegrid.org
atlas.cern.ch
cdarkside.opensciencegrid.org
cdf.opensciencegrid.org
cdms.opensciencegrid.org
cms.cern.ch
cms.osgstorage.org
cms-ib.cern.ch
config-osg.opensciencegrid.org
connect.opensciencegrid.org
coupp.opensciencegrid.org
d0.opensciencegrid.org
des.opensciencegrid.org
des.osgstorage.org
dune.opensciencegrid.org
fermilab.opensciencegrid.org
gm2.opensciencegrid.org
grid.cern.ch
gwosc.osgstorage.org
icarus.opensciencegrid.org
icecube.opensciencegrid.org
lariat.opensciencegrid.org
ligo.osgstorage.org
ligo-containers.opensciencegrid.org
minerva.opensciencegrid.org
minerva.osgstorage.org
minos.opensciencegrid.org
mu2e.opensciencegrid.org
mu2e.osgstorage.org
nexo.opensciencegrid.org
nova.opensciencegrid.org
nova.osgstorage.org
oasis.opensciencegrid.org
sbnd.opensciencegrid.org
seaquest.opensciencegrid.org
sft.cern.ch
singularity.opensciencegrid.org
snoplus.egi.eu
spt.opensciencegrid.org
stash.osgstorage.org
uboone.opensciencegrid.org
uboone.osgstorage.org
veritas.opensciencegrid.org
xenon.opensciencegrid.org
"

REPOS_COMMA_SEP=$(echo $REPOS | xargs | sed -e 's/ /,/g')

cat << EOF | sudo tee /etc/cvmfs/default.local
CVMFS_REPOSITORIES=${REPOS_COMMA_SEP}
CVMFS_QUOTA_LIMIT=20000
CVMFS_HTTP_PROXY=DIRECT
EOF

cvmfs_config probe
```

# cvmfs run docker


```bash

docker run -ti \
  -w ${PWD} \
  -v /cvmfs:/cvmfs \
  -v ${PWD}:${PWD} \
  centos:7  \
  /bin/bash

yum install -y which

# Ihink this command install python packages
pushd /cvmfs/cdms.opensciencegrid.org

#./setup_cdms.sh -L
source setup_cdms.sh V04-10

popd

# check I have all packages

# /cvmfs/cdms.opensciencegrid.org/releases/centos7/V04-08/lib/python3.7/site-packages/CDMSDataCatalog
python -c "import CDMSDataCatalog"

# http://titus.stanford.edu:8080/git/summary/?r=Analysis/pyRawIO.git
# find ./releases/centos7/V04-08 -iname "*rawio*"
# ./releases/centos7/V04-08/lib/python3.7/site-packages/rawio
python -c "import rawio"
```

