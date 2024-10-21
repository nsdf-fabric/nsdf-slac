import os
import re
from utils import (
    BUCKET_PATH,
    MIDFILES_DIR,
    FILE_PATTERN,
    IDX_FILES_DIR,
    PREFIX,
    get_aws_bucket,
    check_if_key_exists,
)
import concurrent


def process_raw_files():
    s3 = get_aws_bucket(True)
    jobs = []
    for _, k in enumerate(s3.objects.limit(42000).filter(Prefix=BUCKET_PATH)):
        full_path = k.key
        mid_file = os.path.basename(full_path)
        if full_path.endswith(".mid.gz") and re.match(FILE_PATTERN, mid_file):
            local_path = f"{MIDFILES_DIR}{mid_file}"
            # download and process file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            jobs.append(mid_file)

    with concurrent.futures.ProcessPoolExecutor(max_workers=128) as ex:
        futures = [ex.submit(process_raw_file, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Error: {e}")


def process_raw_file(file: str):
    """
    Process a mid file from storage
    -------------------------------
    Parameters
    ----------
    file(str): the mid file to process in the the format <filename>.mid.gz
    """
    s3 = get_aws_bucket(True)
    mid_file_name = file.split(".mid")[0]
    mid_prefix = "_".join(mid_file_name.split("_")[:2])

    src = os.path.join(BUCKET_PATH, mid_prefix, file)
    dst = os.path.join(MIDFILES_DIR, file)

    idxfile = os.path.join(PREFIX, mid_file_name, mid_file_name.split(".")[0] + ".idx")
    csvfile = os.path.join(PREFIX, mid_file_name, mid_file_name.split(".")[0] + ".csv")
    txtfile = os.path.join(PREFIX, mid_file_name, mid_file_name.split(".")[0] + ".txt")
    binfile = os.path.join(PREFIX, mid_file_name, "0000.bin")
    # check that the mid file has not been processed

    s3.download_file(src, dst)
    proc = os.popen(f"./channel_extract {MIDFILES_DIR}{file}")
    proc.close()
    os.remove(dst)
    print(f"Processed {mid_file_name}")


def download_processed_files(midfile: str):
    """
    Download processed files from storage (idx, channel metadata, event metadata)
    -----------------------------------------------------------------------------
    Parameters
    ----------
    file(str): the mid file to download in the the format 07180808_1558_F0001
    """
    s3 = get_aws_bucket()

    filenames = [f"{midfile}.idx", f"0000.bin", f"{midfile}.txt", f"{midfile}.csv"]
    download_files = [
        os.path.join(PREFIX, midfile, filenames[0]),
        os.path.join(PREFIX, midfile, filenames[1]),
        os.path.join(PREFIX, midfile, filenames[2]),
        os.path.join(PREFIX, midfile, filenames[3]),
    ]

    for i, file in enumerate(download_files):
        dst = os.path.join(IDX_FILES_DIR, midfile, filenames[i])
        if filenames[i].split(".")[1] == "bin":
            dst = os.path.join(IDX_FILES_DIR, midfile, midfile, filenames[i])

        if not os.path.exists(dst):
            if check_if_key_exists(file, True):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                s3.download_file(file, dst)
            else:
                raise FileNotFoundError(f"{midfile} does not exists in storage")


if __name__ == "__main__":
    process_raw_files()
    pass
