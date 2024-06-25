""" 
main.py
"""

__author__ = "Devansh Parapalli"
__license__ = "MIT"

import json
import os
import re
import sys
from util import boolean_user_choice, user_choice, ANSI
import glob
import pymupdf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from rapidfuzz import fuzz, process, utils

import string

# REGEXES

GAZETTE_REGEX_PATTERN = r"\d\d\d\d\d\d\(\d?\d\.\d\d\)" 
ROLLNO_REGEX = r"(?P<_>Roll\|No\.\|:)(?P<roll>\|[0-9|]{0,6}\|)(?P<__>Gender)"
NAME_REGEX = r"(?P<_>\|Name\|of\|Student\|:)(?P<name>\|[A-Z|]*\|)(?P<__>Mother's)"
EXAM_REGEX = r"(?P<_>\|Exam\|Name\|:)(?P<exam>\|[A-Z|&.()]*\|)(?P<__>Name)"
SESSION_REGEX = r"(?P<_>Session\|:\|)(?P<session>WINTER-\d\d\d\d|SUMMER-\d\d\d\d)(\|)"
# Begin by reading the pdf

choices = glob.glob("*.pdf")
file_selected = choices[user_choice(choices)]


metadata = {}
data = []
doc: pymupdf.Document = pymupdf.open(file_selected)

initial_page = doc[0]
text = "|".join([word[4] for word in initial_page.get_text("words")])
# roll = re.findall(ROLLNO_REGEX, text)[0][1].replace("|", " ").strip()
# name = re.findall(NAME_REGEX, text)[0][1].replace("|", " ").strip()
exam = re.findall(EXAM_REGEX, text)[0][1].replace("|", " ").strip()
session = re.findall(SESSION_REGEX, text)[0][1].replace('|', " ").strip()

metadata["exam"] = exam
metadata["session"] = session
metadata["filename"] = file_selected.split(".")[0]

for page in doc:
    text = "|".join([word[4] for word in page.get_text("words")])
    roll = re.findall(ROLLNO_REGEX, text)[0][1].replace("|", " ").strip()
    name = re.findall(NAME_REGEX, text)[0][1].replace("|", " ").strip()
    data.append({
        "name": name,
        "roll": int(roll),
    })


roll_numbers = [i['roll'] for i in data]

# state vars

ENTIRE_GAZETTE = []
FILTERED_GAZETTE = []

# print(f"{metadata=}, {data=}")

# Setup selenium to get the gazette

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")

with webdriver.Chrome(options=chrome_options) as driver:
    driver.get('https://rtmnuresults.org/')
    driver.maximize_window()
    html = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
    driver.execute_script("document.body.style.zoom='125 %'")
    
    session_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'lblsess')))
    # print(f"{session} == {session_elem.text}?")
    if not (session[0] == session_elem.text[0] and session[-1] == session_elem.text[-1]):
        # Hack for previous exams, there is no way to programmatically find the previous exam button, cuz they putin an image der.
        previous_exam_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ImageButton7'))) # WInter23
        previous_exam_button.click()
        html = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'html')))
        session_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'lblsess')))
        print(f"{session} == {session_elem.text}?")
        if not boolean_user_choice():
            print(f"{ANSI.FAIL}[ERROR] Cannot find the correct session{ANSI.ENDC}")
            sys.exit(1)
    
    faculty_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ddlselectfaculty')))
    Select(faculty_select).select_by_value('1')
    _exam_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ddlselectexam')))
    exam_select = Select(_exam_select)
    options = [i.text for i in exam_select.options]
    
    # Match the exam returned from pdf to one of the options
    _exam = process.extractOne(metadata['exam'], options, scorer=fuzz.token_sort_ratio, processor=utils.default_process)
    print(f"Is this correct: {_exam[0]}?")
    if (boolean_user_choice()):
        exam_select.select_by_index(_exam[-1])
    else:
        _user_exam = input("Enter the correct exam name >")
        _exam = process.extractOne(_user_exam, options, scorer=fuzz.token_sort_ratio, processor=utils.default_process)
        print(f"Is this correct: {_exam[0]}?")
        if boolean_user_choice():
            exam_select.select_by_index(_exam[-1])
        else:
            print(f"{ANSI.FAIL}[ERROR] Cannot find correct examination{ANSI.ENDC}")
            sys.exit(1)
    
    gazette_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'imgbtnexamgazette')))
    gazette_button.click()
    
    gazette_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
    
    gazette_regex = re.compile(GAZETTE_REGEX_PATTERN)
    
    for match in gazette_regex.finditer(gazette_table.text):
        roll_number, sgpa = match.group().replace(')', "").split('(')
        roll_number = int(roll_number.strip())
        sgpa = float(sgpa.strip())
        
        ENTIRE_GAZETTE.append((roll_number, sgpa))

    # Externally Known Scores
    EXTERNALLY_INJECTED = []
    if os.path.exists(f"{metadata['filename']}-known.i.txt"):
        names = [i['name'] for i in data]
        with open(f"{metadata['filename']}-known.i.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith(tuple(string.digits)):
                    roll_number, sgpa = line.split()
                    roll_number = int(roll_number.strip())
                    sgpa = float(sgpa.strip())
                    EXTERNALLY_INJECTED.append(roll_number)
                    ENTIRE_GAZETTE.append((roll_number, sgpa))
                else:
                    _name, sgpa = line.split(',')
                    found = process.extractOne(_name, names, scorer=fuzz.token_sort_ratio, processor=utils.default_process)
                    print(f"Matched {found[0]} with {_name}")
                    is_correct = boolean_user_choice()
                    if not is_correct:
                        print('Skipping')
                        continue
                    roll_number = data[found[-1]]['roll']
                    sgpa = float(sgpa.strip())
                    EXTERNALLY_INJECTED.append(roll_number)
                    ENTIRE_GAZETTE.append((roll_number, sgpa))
    
    GAZETTE_WITHHELD_ENROLLMENT = []
    GAZETTE_WITHHELD_TABULATION = []
    
    try:
        sections = gazette_table.text.split("***")
        enrollment_issues = sections[1].strip()
        tabulation_issues = sections[2].strip()
        
        for match in (re.compile(r'\d{1,6}')).finditer(enrollment_issues):
            roll_number = int(match.group())
            if roll_number in EXTERNALLY_INJECTED:
                continue
            GAZETTE_WITHHELD_ENROLLMENT.append(roll_number)
            ENTIRE_GAZETTE.append((roll_number, -1.0))
        for match in (re.compile(r'\d{1,6}')).finditer(tabulation_issues):
            roll_number = int(match.group())
            if roll_number in EXTERNALLY_INJECTED:
                continue
            GAZETTE_WITHHELD_TABULATION.append(roll_number)
            ENTIRE_GAZETTE.append((roll_number, -2.0))
    except Exception as e:
        print(e)
        pass
    

    
    
    # Filter the gazette to only include the roll numbers that are in the pdf
    for entry in ENTIRE_GAZETTE:
        if entry[0] in roll_numbers:
            FILTERED_GAZETTE.append(entry)
    
    
    unknown = []
    for rn in roll_numbers:
        if rn not in [i[0] for i in FILTERED_GAZETTE]:
            unknown.append((rn, 0.0))
    FILTERED_GAZETTE.extend(unknown)
    
    
    FILTERED_GAZETTE.sort(key=lambda x: -x[1])
    ENTIRE_GAZETTE.sort(key=lambda x: -x[1])
    
    # json.dump(FILTERED_GAZETTE, open(f"{metadata['filename']}-gazette.i.json", "w"))
    
    # merge the results of the pdf and the gazette
    
    for i in data:
        for j in FILTERED_GAZETTE:
            if i['roll'] == j[0]:
                i['sgpa'] = j[1]
    # who cares about 1 extra second used for this shit
    data.sort(key=lambda x: -x['sgpa'])
    roll_numbers = [i['roll'] for i in data]
    global_rank_file = open(f"{metadata['filename']}-global_rank.i.txt", "w")
    print("UNIR) ROLNUM\tSGPA\tNAME")
    print("UNIR) ROLNUM\tSGPA\tNAME", file=global_rank_file)
    for i, entry in enumerate(ENTIRE_GAZETTE):
        roll, sgpa = entry
        name = ""
        if roll in roll_numbers:
            name = data[roll_numbers.index(roll)]['name']
        print(f"{i+1:4}) {roll}\t{sgpa:4}\t{name}")
        print(f"{i+1:4}) {roll}\t{sgpa:4}\t{name}", file=global_rank_file)
    
    driver.execute_script("window.history.go(-1)")
    
    # Folder for saving result images
    folder = f"{metadata['filename']}-result_images"
    if not os.path.exists(folder):
        os.mkdir(folder)
    
    # set to check which ones have been completed
    COMPLETED = set()
    # Begin with an initial condition
    roll_no_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtrollno')))
    roll_no_input.send_keys(str(roll_numbers[0]))
    submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'imgbtnviewmarksheet')))
    submit_button.click()
    
    for i, roll in enumerate(roll_numbers): 
        driver.execute_script("window.history.go(-1)")
        roll_no_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtrollno')))
        roll_no_input.clear()
        roll_no_input.send_keys(str(roll))
        submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'imgbtnviewmarksheet')))
        submit_button.click()
        # Check if invalid
        try:
            Alert(driver).accept()
            print(f"{ANSI.FAIL}[ERROR] {roll} is invalid.{ANSI.ENDC}")
            continue
        except NoAlertPresentException:
            pass
        # wait for the image to load
        image_frame = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ContentPlaceHolder1_ifrm')))
        driver.switch_to.frame(image_frame)
        image = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
        image.screenshot(f'{os.getcwd()}{os.path.sep}{folder}{os.path.sep}{roll}-{data[i]["name"]}.png')
        driver.switch_to.default_content()
        COMPLETED.add(roll)
    
    with open(f"{metadata['filename']}.csv", "w") as f:
        f.write('rank,roll,name,sgpa,error\n')
        for i, d in enumerate(data):
            output = f"{i+1},{d['roll']},{d['name']},{d['sgpa']},"
            if d['roll'] in GAZETTE_WITHHELD_ENROLLMENT:
                output+="Withheld for Enrollment"
            elif d['roll'] in GAZETTE_WITHHELD_TABULATION:
                output+="Withheld for Tabulation"
            elif d['roll'] not in COMPLETED:
                output+="Invalid Roll Number"
            f.write(output + "\n")
        f.write('\n')
    
    with open(f"{metadata['filename']}.o.json", "w") as f:
        json.dump({
            "data": data,
            "metadata": metadata,
            "full_gazette": ENTIRE_GAZETTE,
            "filtered_gazette": FILTERED_GAZETTE,
            "completed": list(COMPLETED),
            "not_completed": list(set(roll_numbers) - COMPLETED),
        }, f)
    