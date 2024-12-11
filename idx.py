import numpy as np
import OpenVisus as ov

FILENAME = "07181009_0953_F0008"


def main():
    # iterate all the npz files create the idx and metadata
    pass


def idx(filepath: str):
    arr = np.load(f"{filepath}.npz")
    N = 0

    f = open(f"{filepath}.txt", "w")
    for k, v in arr.items():
        f.write(f"{k} {N} {N+len(v)}\n")
        N += len(v)
    f.close()

    agg = np.concatenate([v for v in arr.values()])
    db = ov.CreateIdx(
        url=f"{filepath}.idx",
        dims=[4096, len(agg)],
        fields=[ov.Field("data", str(agg.dtype), "row_major")],
        compression="raw",
    )

    db.write(agg, field="data")


idx(FILENAME)
