import pandas as pd
import logging
import re
from string import punctuation

FILE_NAME = "comments.csv"
COL_NAME = "comment"

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


VIET_TEEN = {
    "mk": "mình",
    "mng": "mọi người",
    "k": "không",
    "kg": "không",
    "k0": "không",
    "ko": "không",
    "hg": "hông",
    "trc": "trước",
    "dc": "được",
    "đc": "được",
    "z": "vậy",
}

# LOGGING
FORMAT = "[%(asctime)s] - [%(levelname)s] - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


def comment_filter(comment: str):

    comment = EMOJI_RE.sub(r"", comment)

    return comment


def line_filter(line: str):
    return line


def word_filter(word: str):

    # Remove URL
    if word.startswith("http"):
        return ""

    # Remove basic emoji:
    if word.startswith(":"):
        return ""

    # Random word
    if len(word) > 12:
        return ""

    # Punction
    if word in punctuation:
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
            chars = word.split()
            # for cidx in range(len(chars)):
            #     chars[cidx] = char_filter(chars[cidx])
            words[widx] = "".join([c for c in chars if c])
        lines[lidx] = " ".join([w for w in words if w])
    return "\n".join(lines)


def main():
    df = (
        pd.read_csv(FILE_NAME, index_col=False)
        .dropna(subset=[COL_NAME])
        .reset_index(drop=True)
    )

    for row in range(0, 1000):
        df.loc[row, COL_NAME] = clean(df.loc[row, COL_NAME]).strip()

    df[:1000][df[:1000][COL_NAME].astype(bool)].dropna(subset=[COL_NAME]).reset_index(
        drop=True
    ).to_csv("comments_parsed.csv", index=False)


if __name__ == "__main__":
    main()
