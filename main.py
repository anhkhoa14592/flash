"""
usage: [-h] [-r REF] [-f FILE] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -r REF, --reference REF
                        Choose the kind of dictionary as reference. Support [oxf, cambr] only, default is cambr
  -f FILE, --file FILE  File name need to perform
  -o OUTPUT, --ouput OUTPUT
                        Output result filename

"""
import argparse
import requests
import time
import re

# Configuration for request
DELAY = 0
URL = "https://dictionary.cambridge.org/vi/dictionary/english/"
HEADER = {
    "Referer": "https://dictionary.cambridge.org/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0",
    "X-API-SOURCE": "PC",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}

"""
Read lines for files
return: list of line
"""


def read_file(filename):
    with open(filename) as f:
        lines = f.readlines()

    lines = [x.strip() for x in lines]  # Remove breakline at the end of each line

    return lines


def fix_tense(word, origin, transcription):
    if origin == word:
        return transcription

    if word[len(word) - 2:] == "ed" or word[len(word) - 1:] == "d":
        if transcription[len(transcription) - 1:] in ["s", "p", "k", "f", "ʃ", "tʃ"]:
            transcription = transcription + "t"
        elif transcription[len(transcription) - 2:] in ["t", "d"]:
            transcription = transcription + "id"
        else:
            transcription = transcription + "d"
    if word[len(word) - 2:] == "es" or word[len(word) - 1:] == "s":
        if transcription[len(transcription) - 1:] in ["p", "k", "t", "f", "θ"]:
            transcription = transcription + "s"
        elif transcription[len(transcription) - 2:] in ["tʃ", "s", "ʃ", "z", "ʒ", "dʒ"]:
            transcription = transcription + "iz"
        else:
            transcription = transcription + "z"

    # print(word, origin, transcription)

    return transcription


"""
Extract word by word from each line by based on whitespace, then make transcription.
return: list of transcription.
"""


def make_transcription(lines):
    transcription_lines = list()

    for line in lines:
        list_of_words = line.split(" ")
        transcription_line = ""
        for word in list_of_words:

            # remove sepecial character in string like : " , etc.
            w = ""
            for c in word:
                if c.isalnum():
                    w += c

            word = w

            r = requests.get(url=URL + word, headers=HEADER)
            origin, transcription = extract_transcription(r)

            # In case not found transcription, keep original word
            if transcription:
                transcription = fix_tense(word=word, origin=origin,
                                          transcription=transcription)  # Fixing case having s, es, d or ed
                transcription_line = transcription_line + transcription + " "
            else:
                transcription_line = transcription_line + word + " "

            print(origin)
            print(transcription)

            time.sleep(DELAY)  # Bypass rate limit

        transcription_lines.append(transcription_line)
    return transcription_lines


"""
Extract transcription from response HTML using rexp
return: string
"""


def extract_transcription(response):
    pattern = "/<span class=\"ipa dipa lpr-2 lpl-1\">(\S+)</span>/"  # This pattern is used for transcription
    ori_pattern = "<span class=\"hw dhw\">(\S+)</span></span>"  # This pattern is used for matched word

    matched = re.search(pattern=pattern, string=response.text)
    ori_matched = re.search(pattern=ori_pattern, string=response.text)

    if matched:
        return ori_matched.group(1), matched.group(1)
    else:
        return None, None


"""
Write to file the result
"""


def write_to_file(lines, trans_lines, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line)
            f.write("\n")  # Break line each line

        f.write("\n---\n")  # Break line between original and transcription

        for trans_line in trans_lines:
            f.write(trans_line)
            f.write("\n")  # Break line each line


if __name__ == '__main__':
    parser = argparse.ArgumentParser("")
    parser.add_argument("-r", "--reference", dest="ref",
                        help="Choose the kind of dictionary as reference. Support [oxf, cambr] only, default is cambr",
                        type=str,
                        default="cambr")
    parser.add_argument("-f", "--file", dest="file", help="File name need to perform", type=str)
    parser.add_argument("-o", "--ouput", dest="output", help="Output result filename", type=str)
    args = parser.parse_args()

    if args.ref:
        ref = args.ref
    if args.file:
        file = args.file
        output = args.file + "_output.txt"
    if args.output:
        output = args.output

    lines = read_file(filename=file)
    trans_lines = make_transcription(lines=lines)

    write_to_file(lines=lines, trans_lines=trans_lines, filename=output)
