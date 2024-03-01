import boto3, concurrent, traceback
from botocore.client import Config
import os,sys,subprocess
from pprint import pprint

import boto3.session
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import urllib3
urllib3.disable_warnings()

src_prefix="CDMS/UMN"
src_endpoint_url="https://ncsa.osn.xsede.org"
src_bucket_name="supercdms-data"

dst_prefix="supercdms-data"
dst_endpoint_url='https://maritime.sealstorage.io/api/v0/s3'
dst_bucket_name="utah"

def Connect(profile_name,endpoint_url,bucket_name, verify=True):
	session=boto3.session.Session(profile_name=profile_name)
	resource=session.resource('s3', endpoint_url=endpoint_url,verify=verify)
	bucket = resource.Bucket(bucket_name)
	client = session.client('s3', endpoint_url=endpoint_url, verify=verify)
	return dict(session=session, resource=resource, bucket=bucket, client=client)

ConnectSrc=lambda : Connect(profile_name='slac_private',endpoint_url=src_endpoint_url, bucket_name=src_bucket_name)
ConnectDst=lambda : Connect(profile_name='sealstorage', endpoint_url=dst_endpoint_url, bucket_name=dst_bucket_name, verify=False)

# ////////////////////////////////////////////////////////////////
def Shell(cmd):
	return subprocess.check_output(cmd, shell=True, text=True)

# ////////////////////////////////////////////////////////////////
def Upload(src_key, local_filename, dst_key, done_filename):

	#  remove from another run
	if os.path.isfile(local_filename):
		os.remove(local_filename)

	src=ConnectSrc()
	dst=ConnectDst()

	os.makedirs(os.path.dirname(local_filename),exist_ok=True)

	# download the file
	src['bucket'].download_file(src_key, local_filename)

	# upload file with the checksum
	cksum=int(Shell(f'cksum {local_filename}').split()[0].strip())
	dst['bucket'].upload_file(local_filename,  dst_key, ExtraArgs={"Metadata": { "checksum": str(cksum)}})

	# check the checksum
	assert(dst['client'].head_object(Bucket=dst['bucket'].name,Key=dst_key)["Metadata"]["Checksum"]==str(cksum))

	# don't do again
	Shell(f'touch {done_filename}')
	os.remove(local_filename)
	print("Done",f"s3://{src['bucket'].name}/{src_key}", local_filename, f"s3://{dst['bucket'].name}/{dst_key}")


# ////////////////////////////////////////////////////////////////
if __name__=="__main__":

	print("Collecting files")
	jobs=[]
	tot=0
	for it in ConnectSrc()['bucket'].objects.filter(Prefix=src_prefix):
		src_key=it.key
		if src_key.endswith(".mid.gz"):
			local_filename=f"{dst_prefix}/{src_key}"
			dst_key=f"{dst_prefix}/{src_key}"
			done_filename=f"{local_filename}.done"
			tot+=1
			if os.path.isfile(done_filename):
				print("Skipping",src_key, "since already done")
				continue
			jobs.append([Upload, src_key,local_filename,dst_key,done_filename])
	print(f"Found {len(jobs)} new jobs out of {tot}")

	todo=tot
	with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
		futures = [executor.submit(*job) for job in jobs]
		for future in concurrent.futures.as_completed(futures):
			todo-=1
			print(f"Still todo {todo}")


