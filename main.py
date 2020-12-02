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
DELAY = 1
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
            r = requests.get(url=URL + word, headers=HEADER)
            transcription = extract_transcription(r)

            # In case not found transcription, keep original word
            if transcription:
                transcription_line = transcription_line + transcription + " "
            else:
                transcription_line = transcription_line + word + " "

            time.sleep(DELAY)  # Bypass rate limit

        transcription_lines.append(transcription_line)
    return transcription_lines


"""
Extract transcription from response HTML using rexp
return: string
"""


def extract_transcription(response):
    pattern = "/<span class=\"ipa dipa lpr-2 lpl-1\">(\S+)</span>/"
    matched = re.search(pattern=pattern, string=response.text)
    if matched:
        return (matched.group(1))
    else:
        return None


"""
Write to file the result
"""


def write_to_file(lines, trans_lines, filename):
    with open(filename, "w") as f:
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
