import os
import stat
import argparse
import csv
import collections
import traceback
import tqdm
import gzip
import pickle


def stat_all(root_folder, outputfile):
    to_stat = collections.deque()
    to_stat.append(root_folder)

    # writer = csv.writer(outputfile)
    files = []

    root_dev = os.lstat(root_folder).st_dev

    cur = 0

    with tqdm.tqdm() as t:
        while len(to_stat) > 0:
            cur += 1
            if cur % 1000 == 0:
                t.update(cur//1000)
            # next_to_stat = to_stat.popleft()
            next_to_stat = to_stat.pop()

            try:
                stat_result = os.lstat(next_to_stat)
            except Exception:
                traceback.print_exc()
            if stat_result.st_dev != root_dev:
                continue
            files.append(
                (
                    next_to_stat,
                    stat_result.st_mode,
                    stat_result.st_ino,
                    stat_result.st_dev,
                    stat_result.st_nlink,
                    stat_result.st_uid,
                    stat_result.st_gid,
                    stat_result.st_size,
                    stat_result.st_atime,
                    stat_result.st_mtime,
                    stat_result.st_ctime,
                    stat_result.st_blocks,
                    stat_result.st_blksize
                )
            )

            try:
                if stat.S_ISDIR(stat_result.st_mode):
                    to_stat.extend(
                        [os.path.join(next_to_stat, d) for d in os.listdir(next_to_stat)][::-1]
                    )
            except Exception:
                traceback.print_exc()

    with gzip.open(outputfile, "wb") as fout:
        pickle.dump(files, fout)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root", default="/", required=False)
    args = parser.parse_args()

    # with open("result.csv", "wt", newline="") as fout:
    #     stat_all(args.root, fout)
    stat_all(args.root, "result.pkl.gz")


if __name__ == "__main__":
    main()
