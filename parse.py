from numpy import isin
import pandas as pd
import logging
import re
from string import punctuation

FILE_NAME = "comments.csv"
COL_NAME = "comment"
TEST_LIMIT = -1

EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002500-\U00002BEF"  # chinese char
    "\U00002702-\U000027B0"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"  # dingbats
    "\u3030"
    "]+",
    re.UNICODE,
)

LISTING_STYLE = ["-", "+"]


VIET_TEEN = {
    "mk": "mình",
    "mik": "mình",
    "m": "mình",
    "mng": "mọi người",
    "mn": "mọi người",
    "m.ng": "mọi người",
    "k": "không",
    "kg": "không",
    "k0": "không",
    "ko": "không",
    "kh": "không",
    "hg": "hông",
    "hok": "hông",
    "trc": "trước",
    "dc": "được",
    "đc": "được",
    "đk": "được",
    "z": "vậy",
    "nt": "nhắn tin",
    "hnay": "hôm nay",
    "dt": "điện thoại",
    "đt": "điện thoại",
    "đth": "điện thoại",
    "tgdd": "thế giới di động",
    "ntn": "như thế nào",
    "vch": "vãi cả hang",
    "sp": "sản phẩm",
    "spham": "sản phẩm",
    "nma": "nhưng mà",
    "nhma": "nhưng mà",
    "kp": "không phải",
    "rep": "trả lời",
    "hag": "hàng",
    "òi": "rồi",
    "r": "rồi",
    "lm": "làm",
    "ae": "anh em",
    "bnhiu": "bao nhiêu",
    "í": "ấy",
    "đgia": "đại gia",
    "kb": "không biết",
    "vid": "video",
    "vl": "vãi l",
    "cmn": "con me no",
    "ms": "mới",
    "chx": "chưa",
    "đvvc": "đơn vị vận chuyển",
    "b": "bạn",
    "1tg": "một thời gian",
    "sd": "sử dụng",
    "vs": "với",
    "cx": "cũng",
    "cg": "cũng",
    "cskh": "chăm sóc khách hàng",
    "tc": "tính chất",
    "tg": "thời gian",
    "thgian": "thời gian",
    "nv": "nhân viên",
    "nvien": "nhân viên",
    "ad": "nhân viên",
    "lquan": "liên quan",
    "nchug": "nói chung",
    "trl": "trả lời",
    "tl": "trả lời",
    "lg": "lượng",
    "ib": "liên lạc",
    "j": "gì",
    "hdsd": "hướng dẫn sử dụng",
    "tq": "trung quốc",
    "sx": "sản xuất",
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
}

SPECIAL_CASE = frozenset(
    (
        "T.T",
        "^^",
        "(ര̀ᴗര́)و",
        "(ര̀ᴗര́)و",
        "(ര̀ᴗര́)و",
        "(ര̀ᴗര́)و",
        "(ര̀ᴗര́)و",
        "(ര̀ᴗര́)و",
        "(•ᴗ•)",
        "<3",
        "[^•°]",
    )
)

DUPLICATE_END = frozenset(("n", "g", "c", "m", "u", "y", "h", "i", "h", "z"))

# LOGGING
FORMAT = "[%(asctime)s] - [%(levelname)s] - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


def comment_filter(comment: str):

    comment = EMOJI_RE.sub(r"", comment)

    return comment


def line_filter(line: str):

    # Clean listing style
    for style in LISTING_STYLE:
        line = line.lstrip(style)
    line.lstrip()

    return line


def word_filter(word: str):

    # Remove URL
    if word.startswith("http"):
        return ""

    # Remove basic emoji:
    if word.startswith(":") or word.startswith("="):
        return ""

    # Random word
    if len(word) > 12:
        return ""

    # # Punction
    # if word in punctuation:
    #     return ""

    # Map teen code
    if VIET_TEEN.get(word.lower()):
        return VIET_TEEN[word.lower()].split()

    # Map teen code with punction
    tmp = word
    while tmp and tmp[-1] in punctuation:
        tmp = tmp[:-1]
    if VIET_TEEN.get(tmp.lower()):
        return word.replace(tmp, VIET_TEEN[tmp.lower()]).split()

    # Remove trailing end
    if len(word) > 3 and word[-1] == word[-2] and word[-1] in DUPLICATE_END:
        while len(word) > 3 and word[-1] == word[-2]:
            word = word[:-1]

    if word in SPECIAL_CASE:
        return ""

    return word


def char_filter(char: str):
    return char


def clean(comment):
    comment = comment_filter(comment)
    lines = comment.split("\n")
    for lidx in range(len(lines)):
        line = line_filter(lines[lidx])
        words = line.split()
        for widx in range(len(words)):
            word = word_filter(words[widx])
            # word = words[widx]
            if isinstance(word, list):
                words[widx] = " ".join(word)
            else:
                chars = word.split()
                # for cidx in range(len(chars)):
                #     chars[cidx] = char_filter(chars[cidx])
                words[widx] = "".join(chars)
        lines[lidx] = " ".join(words)
    return "\n".join(lines)


def main():
    df = (
        pd.read_csv(FILE_NAME, index_col=False)
        .dropna(subset=[COL_NAME])
        .reset_index(drop=True)
    )

    if TEST_LIMIT > 0:
        for row in range(0, TEST_LIMIT):
            df.loc[row, COL_NAME] = clean(df.loc[row, COL_NAME]).strip()
        df[:TEST_LIMIT][df[:TEST_LIMIT][COL_NAME].astype(bool)].reset_index(
            drop=True
        ).to_csv("comments_parsed.csv", index=False)
    else:
        for row in range(0, df.shape[0]):
            df.loc[row, COL_NAME] = clean(df.loc[row, COL_NAME]).strip()
        df[df[COL_NAME].astype(bool)].reset_index(drop=True).to_csv(
            "comments_parsed.csv", index=False
        )


if __name__ == "__main__":
    main()
