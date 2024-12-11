import os
import numpy as np
import OpenVisus as ov

NPZ_FILES_DIR = "./mid_npz/"
IDX_FILES_DIR = "./idx/"


def main():
    if not os.path.exists(IDX_FILES_DIR):
        os.mkdir(IDX_FILES_DIR)

    # iterate all the npz files create the idx and metadata
    for file in os.listdir(NPZ_FILES_DIR):
        filename = file.split(".npz")[0]
        if os.path.exists(f"{IDX_FILES_DIR}{filename}.idx"):
            continue
        idx(filename)


def idx(filename: str):
    arr = np.load(f"{NPZ_FILES_DIR}{filename}.npz")
    N = 0

    f = open(f"{IDX_FILES_DIR}{filename}_metadata.txt", "w")
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


main()
