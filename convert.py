import os,sys,boto3,json,xmltodict,itertools,subprocess
from botocore.client import Config
import midas.file_reader
from pprint import pprint
import numpy as np

import urllib3
urllib3.disable_warnings()

# /////////////////////////////////////////
def GetBanksData(filename):
	reader = midas.file_reader.MidasFile(filename)
	for E,evt in enumerate(reader):
		for bank_name, bank in evt.banks.items():
			yield (evt, bank)


# /////////////////////////////////////////
def ParseEvent(evt):
	ret={}
	ret["header"]={
		"event_id": evt.header.event_id,	# int
		"trigger_mask": evt.header.trigger_mask,	# int
		"serial_number":evt.header.serial_number,	# int
		"timestamp": evt.header.timestamp,	# int UNIX timestamp of event
		"event_data_size_bytes": evt.header.event_data_size_bytes,	# int Size of all banks
	}
	ret["all_bank_size_bytes"]=evt.all_bank_size_bytes	# (int)
	ret["flags"]=evt.flags
	ret["non_bank_data"]=evt.non_bank_data # (bytes or None) - Content of some special events that don't
	
	ret["banks"]={}
	for bank_name, bank in evt.banks.items():
		ret["banks"][bank.name]={
			"name": bank.name,	# (str) - 4 characters
			"type": bank.type,	# (int) - See `TID_xxx` members in `midas` module
			"size_bytes": bank.size_bytes,	# (int)
			"data": bank.data # (tuple of int/float/byte etc, or a numpy array if use_numpy is specified when unpacking),
		}
	return ret

# ////////////////////////////////////////////////////////////////
def Shell(cmd):
	return subprocess.check_output(cmd, shell=True, text=True)

# /////////////////////////////////////////
def Connect(profile_name,endpoint_url,bucket_name, verify=True):
	session=boto3.session.Session(profile_name=profile_name)
	resource=session.resource('s3', endpoint_url=endpoint_url,verify=verify)
	bucket = resource.Bucket(bucket_name)
	client = session.client('s3', endpoint_url=endpoint_url, verify=verify)
	return dict(session=session, resource=resource, bucket=bucket, client=client)


# /////////////////////////////////////////
def ParseXML(body):
	d=xmltodict.parse(body) 
	assert(isinstance(d,dict))
	return d

# /////////////////////////////////////////
def SaveXML(filename, data):
	os.makedirs(os.path.dirname(filename),exist_ok=True)
	with open(filename,"wb") as out: out.write(data)

# /////////////////////////////////////////
def SaveBinary(filename, data):
	os.makedirs(os.path.dirname(filename),exist_ok=True)
	with open(filename,"wb") as out: out.write(data)

# /////////////////////////////////////////
def SaveArray(filename, data):
	os.makedirs(os.path.dirname(filename),exist_ok=True)
	np.savez_compressed(filename, data=data)

# /////////////////////////////////////////
def SaveJSON(filename,d):
	os.makedirs(os.path.dirname(filename),exist_ok=True)
	with open(filename,"w") as out:
		out.write(d)

# ///////////////////////////////////////////////////////////////
def ConvertJob(K,key):

	import time
	t1=time.time()
	key_noext=key.replace(".mid.gz","")
	
	print("Doing",K, key)
			 
	# download file
	os.makedirs(os.path.dirname(key),exist_ok=True)
	bucket.download_file(key,key)
	# print(f"Downloaded file {key} {os.path.getsize(key)}")

	# generate JSON, save xml cand binary data
	reader = midas.file_reader.MidasFile(key)
	events=[]
	for E,evt in enumerate(reader):
		parsed=ParseEvent(evt)
		non_bank_data=parsed["non_bank_data"]

		# ________________________________ non_bank_data
		if non_bank_data:
			# parse xml
			if non_bank_data[0:5]==b"<?xml":
				sub_key=f"{key_noext}/events/{E:05d}/non_bank_data.xml"
				SaveXML(sub_key,non_bank_data)
				bucket.upload_file(sub_key,	sub_key)
				# print("Uploaded xml file",sub_key,os.path.getsize(sub_key))
				# os.remove(sub_key)
			else:
				sub_key=f"{key_noext}/events/{E:05d}/non_bank_data.bin"
				SaveBinary(sub_key,non_bank_data)
				bucket.upload_file(sub_key,	sub_key)
				# print("Uploaded binary file",sub_key,os.path.getsize(sub_key))
				# os.remove(sub_key)
			parsed["non_bank_data"]={"key":sub_key}
		else:
			del parsed["non_bank_data"]

		# ________________________________ bank data
		for bank_name, bank in parsed["banks"].items():
			data=bank["data"]
			if data: 
				data=np.array(data)
				sub_key=f"{key_noext}/events/{E:05d}/banks/{bank_name}/data.npz"
				SaveArray(sub_key,data)
				bucket.upload_file(sub_key,	sub_key)
				# print("Uploaded data",sub_key,os.path.getsize(sub_key))
				os.remove(sub_key)
				bank["data"]={
					"key":	 sub_key, 
					"shape": str(data.shape),
					"dtype": str(data.dtype),
					"vmin":	str(np.min(data)),
					"vmax":	str(np.max(data))
				} 
			else:
				del bank["data"]
				
		events.append(parsed)

	# save json
	d=json.dumps(events, sort_keys=False, indent=2)
	json_filename=f"{key_noext}.json"
	SaveJSON(json_filename,d)

	# compressed JSON
	Shell(f"gzip --keep --force {json_filename}")
	gz_filename=json_filename+".gz"
	bucket.upload_file(gz_filename,	gz_filename)
	# print("Uploaded json file",gz_filename,os.path.getsize(gz_filename))
	os.remove(gz_filename)

	# to avoid to run the same job over and over
	done_filename=f"{key_noext}.done"
	Shell(f"touch {done_filename}")

	# cannot afford to keep all midas files around
	os.remove(key)
	print("Done",K, key,f"in {time.time()-t1} seconds")

# ////////////////////////////////////////////////////////////////
if __name__=="__main__":

	endpoint_url="https://maritime.sealstorage.io/api/v0/s3"

	# download list of files
	os.makedirs("supercdms-data",exist_ok=True)
	if not os.path.isfile("supercdms-data/list.txt"):
		Shell(f"aws s3 --profile slac_public --endpoint-url {endpoint_url} --no-verify-ssl ls --recursive s3://utah/supercdms-data/CDMS/UMN/R68/Raw/ | grep '.mid.gz'	| awk '{print $4}' > supercdms-data/list.txt")

	conn=Connect(profile_name="sealstorage", endpoint_url=endpoint_url, bucket_name="utah", verify=False)
	bucket=conn['bucket']

	with open("supercdms-data/list.txt","r") as f:
		files=[it.strip() for it in f.readlines() if it.strip().endswith(".mid.gz")]
	print("found",len(files),".mid.gz files")

	jobs=[]
	tot=0
	for K,key in enumerate(files):
		key_noext=key.replace(".mid.gz","")
		done_filename=f"{key_noext}.done"
		tot+=1
		if os.path.isfile(done_filename): 
			continue
		jobs.append((K,key,))

	print(f"Found {len(jobs)} new jobs out of {tot}")

	# ConvertJob(*jobs[0])
	import concurrent
	todo=len(jobs)
	with concurrent.futures.ProcessPoolExecutor (max_workers=64) as executor:
		futures = [executor.submit(ConvertJob, *job) for job in jobs]
		for future in concurrent.futures.as_completed(futures):
			todo-=1
			try:
				result = future.result()
				# print(f"Still todo {todo}")
			except Exception as ex:
				print(f'Error {ex}')


	