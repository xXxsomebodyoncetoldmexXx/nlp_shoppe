import requests
import json
import pandas as pd
import pathlib
import logging
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from copy import copy
from pprint import pprint

URL = "https://shopee.vn/api/v2/item/get_ratings"
GLOBAL_PARAMS = {
    "filter": 1,
    "flag": 1,
}
FILE_NAME = "comments_data.csv"
TOTAL_LIMIT = 100_000
HARD_LIMIT = 1_000
SOFT_LIMIT = 200
SAVE_PREV = True
CHUNK_SIZE = 50

SS = requests.Session()

# LOGGING
FORMAT = "[%(asctime)s] - [%(levelname)s] - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


def get_id(sid_iid):
    shopid, itemid = sid_iid.strip().split(".")
    itemid = itemid.split()[0]
    return {"itemid": itemid, "shopid": shopid}


def json_to_csv(json_data):
    rating_list = []
    comment_list = []
    for rating in json_data["data"]["ratings"]:
        rating_list.append(rating["rating_star"])
        comment_list.append(rating["comment"])

    if SAVE_PREV:
        with open("prev.txt", "a") as f:
            f.write(json.dumps(json_data["data"]["ratings"], ensure_ascii=False) + "\n")

    return {"comment": comment_list, "star": rating_list}


def save_to_file(content):
    header = False if pathlib.Path(FILE_NAME).exists() else True
    mode = "w" if header else "a"
    df = pd.DataFrame(content)
    df.to_csv(FILE_NAME, encoding="utf-8", mode=mode, header=header, index=False)


def get_comment_chunk(id, offset, limit=CHUNK_SIZE, type=0):
    """
    max limit is CHUNK_SIZE
    """
    params = copy(GLOBAL_PARAMS)
    params.update(id)
    params["limit"] = limit
    params["offset"] = offset
    params["type"] = type

    logging.info(f"\tGetting {limit} comment at offset {offset}")

    r = SS.get(URL, params=params)
    content = json.loads(r.content)
    if content["data"]["ratings"]:
        save_to_file(json_to_csv(content))
    return len(content["data"]["ratings"])


def get_comment(id):
    logging.info(f"Fetching comment at {id}")
    total = 0
    star = 1  # start at 1 star and go up
    slimit = SOFT_LIMIT
    hlimit = HARD_LIMIT
    chunk = 0
    while hlimit > 0:
        ret = get_comment_chunk(id, chunk, type=star)
        total += ret
        slimit -= ret
        hlimit -= ret
        chunk += CHUNK_SIZE

        if not ret or slimit <= 0:
            logging.info(f"\t\tGot {SOFT_LIMIT - slimit} comment of {star} star!")
            star += 1
            slimit = SOFT_LIMIT
            chunk = 0

        if star > 5:
            break

    logging.info(f"==>Finish getting {total} comments\n")
    return total


def main():
    global TOTAL_LIMIT

    start = time.time()
    with open("code.txt", "r") as f:
        ids = [get_id(line) for line in f.readlines()]

    idx = 0
    while TOTAL_LIMIT > 0 and idx < len(ids):
        TOTAL_LIMIT -= get_comment(ids[idx])
        idx += 1
    end = time.time()
    dt1 = datetime.fromtimestamp(start)
    dt2 = datetime.fromtimestamp(end)
    diff = relativedelta(dt2, dt1)
    print(
        f"Script run in {diff.hours} hours, {diff.minutes} minutes and {diff.seconds} seconds"
    )


if __name__ == "__main__":
    main()
