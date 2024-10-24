import numpy as np


def main():
    arr = np.load("./out.npz")

    for k, v in arr.items():
        print(k, v)


main()
