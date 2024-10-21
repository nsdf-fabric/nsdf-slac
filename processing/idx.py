import os
import numpy as np
import OpenVisus as ov
from utils import IDX_FILES_DIR, NPZ_FILES_DIR
import concurrent.futures


def main():
    if not os.path.exists(IDX_FILES_DIR):
        os.mkdir(IDX_FILES_DIR)

    # iterate all the npz files create the idx and metadata
    jobs = []
    for file in os.listdir(NPZ_FILES_DIR):
        filename = file.split(".npz")[0]
        if os.path.exists(f"{IDX_FILES_DIR}{filename}.idx"):
            continue
        jobs.append(f"{NPZ_FILES_DIR}{file}")

    with concurrent.futures.ProcessPoolExecutor(max_workers=128) as ex:
        futures = [ex.submit(generate_idx, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Error: {e}")


def generate_idx(file: str):
    """
    Parameters
    ----------
    file(str): the path to the npz file to convert to idx in the the format <filename>.npz
    """
    arr = np.load(file)
    filename = os.path.basename(file).split(".npz")[0]
    N = 0

    f = open(f"{IDX_FILES_DIR}{filename}.txt", "w")
    for k, v in arr.items():
        f.write(f"{k} {N} {N+len(v)}\n")
        N += len(v)
    f.close()

    agg = np.concatenate([v for v in arr.values()])
    db = ov.CreateIdx(
        url=f"{IDX_FILES_DIR}{filename}.idx",
        dims=[4096, len(agg)],
        fields=[ov.Field("data", str(agg.dtype), "row_major")],
        compression="raw",
    )

    db.write(agg, field="data")
    db.compressDataset(["zip"])
    os.remove(file)
    print(f"Converted: {filename}")


if __name__ == "__main__":
    main()
