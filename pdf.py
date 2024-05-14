"""
Exports read_pdf, used to read a RTMNU Admit Card PDF, extract info and return as a 
```py
(
    metadata: {metadata...}
    [data...]
)
```
"""

__author__ = "Devansh Parapalli"
__license__ = "MIT"

import pymupdf
import glob
import re

from util import user_choice

ROLLNO_REGEX = r"(?P<_>Roll\|No\.\|:)(?P<roll>\|[0-9|]{0,6}\|)(?P<__>Gender)"
NAME_REGEX = r"(?P<_>\|Name\|of\|Student\|:)(?P<name>\|[A-Z|]*\|)(?P<__>Mother's)"
EXAM_REGEX = r"(?P<_>\|Exam\|Name\|:)(?P<exam>\|[A-Z|&.()]*\|)(?P<__>Name)"

def main():
    # Choose PDF file for execution
    
    choices = glob.glob("*.pdf")
    file_selected = choices[user_choice(choices)]
    
    
    doc: pymupdf.Document = pymupdf.open(file_selected)
    initial_page = doc[0]
    text = "|".join([word[4] for word in initial_page.get_text("words")])
    roll = re.findall(ROLLNO_REGEX, text)[0][1].replace("|", " ").strip()
    name = re.findall(NAME_REGEX, text)[0][1].replace("|", " ").strip()
    exam = re.findall(EXAM_REGEX, text)[0][1].replace("|", " ").strip()
    
    # print(text, file=open("test.i.txt", "w"))
    print(f"{name=}, {roll=}, {exam=}")


def read_pdf(filename: str) -> tuple[dict, list[dict]]:
    metadata = {}
    data = []
    doc: pymupdf.Document = pymupdf.open(filename)
    
    initial_page = doc[0]
    text = "|".join([word[4] for word in initial_page.get_text("words")])
    # roll = re.findall(ROLLNO_REGEX, text)[0][1].replace("|", " ").strip()
    # name = re.findall(NAME_REGEX, text)[0][1].replace("|", " ").strip()
    exam = re.findall(EXAM_REGEX, text)[0][1].replace("|", " ").strip()
    
    metadata["exam"] = exam
    metadata["filename"] = filename.split(".")[0]

    for page in doc:
        text = "|".join([word[4] for word in page.get_text("words")])
        roll = re.findall(ROLLNO_REGEX, text)[0][1].replace("|", " ").strip()
        name = re.findall(NAME_REGEX, text)[0][1].replace("|", " ").strip()
        data.append({
            "name": name,
            "roll": int(roll),
        })
    
    return metadata, data

if __name__ == "__main__":
    main()
