import os, subprocess
from collections import defaultdict, deque
from utils import (
    METADATA_DIR,
    IDX_FILES_DIR,
    MID_PATTERN,
    PREFIX,
    get_aws_bucket,
    check_if_key_exists,
)
import shutil
from typing import DefaultDict
import concurrent.futures
import re


def Shell(cmd):
    return subprocess.check_output(cmd, shell=True, text=True)


def main():
    # add new files
    jobs = []
    for file in os.listdir(IDX_FILES_DIR):
        file_path = os.path.join(IDX_FILES_DIR, file)
        if os.path.isdir(file_path):
            jobs.append([batch_upload, file_path, file])
        else:
            continue

    with concurrent.futures.ProcessPoolExecutor(max_workers=128) as ex:
        futures = [ex.submit(*job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"error: {e}")

    # cleanup
    shutil.rmtree("./mid_npz")
    shutil.rmtree("./idx")
    shutil.rmtree("./metadata")


def batch_upload(file_path: str, file: str):
    filepaths = [
        f"{file_path}/0000.bin",
        f"{file_path}.idx",
        f"{file_path}.txt",
        f"{METADATA_DIR}/{file}.csv",
    ]

    for p in filepaths:
        upload_file(p)

    for p in filepaths:
        os.remove(p)


def upload_file(filepath: str):
    s3 = get_aws_bucket()
    filename = os.path.basename(filepath)
    fileID = (
        filename.split(".")[0] if filename != "0000.bin" else filepath.split("/")[-2]
    )
    key = os.path.join(PREFIX, fileID, filename)
    if not check_if_key_exists(key, True):
        cksum = int(Shell(f"cksum {filepath}").split()[0].strip())
        s3.upload_file(filepath, key, ExtraArgs={"Metadata": {"checksum": str(cksum)}})
        print(f"uploading {key}, cksum: {cksum}")


def get_uploaded_files() -> DefaultDict[str, int]:
    txt_file = open("./uploaded_files.txt")
    uploaded_files = defaultdict(int)
    if os.path.exists("./uploaded_files.txt"):
        for line in txt_file:
            filename = line.strip()
            uploaded_files[filename]
    txt_file.close()
    return uploaded_files


def write_uploaded_files(q: deque):
    with open("./uploaded_files.txt", "a") as f:
        while q:
            mid_file = q.popleft()
            f.write(f"{mid_file}\n")
        f.close()


def update_uploaded_files():
    s3 = get_aws_bucket()
    q = deque()
    uploaded = get_uploaded_files()
    for _, k in enumerate(s3.objects.filter(Prefix=PREFIX)):
        full_path = k.key
        mid_file = os.path.basename(full_path).split(".")[0]
        if re.match(MID_PATTERN, mid_file) and mid_file not in uploaded:
            uploaded[mid_file]
            q.append(mid_file)

    write_uploaded_files(q)


if __name__ == "__main__":
    main()
    pass
