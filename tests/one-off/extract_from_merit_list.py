import pymupdf

pdf_path = "./tests/one-off/merit-list.pdf"

doc: pymupdf.Document = pymupdf.open(pdf_path)

# print(pdf[0].get_text("dict"))

names0 = None  # column names for comparison purposes
all_extracts = []  # all table rows go here

for page in doc:  # iterate over the pages
    tabs = page.find_tables()  # find tables on page
    for tab in tabs:
        header = tab.header  # get its header
        external = header.external  # header outside table body?
        names = header.names  # column names
        if page.number == 0:  # on first page, store away column names
            names0 = names
        extract = tab.extract()  # get text for all table cells
        all_extracts.extend(extract)  # append to total list

# print(f"The joined table has {len(all_extracts)} rows and {len(names0)} columns.\n")
# print(names0)
comp_students = []
for i, r in enumerate(all_extracts):
    comp_students.append((r[1], r[2])) if (r[0].isdigit() and r[-1] in ['Computer', 'computer']) else None
    # if i >= 10:
        # print("...")
        # break
print(f"Found {len(comp_students)} computer students.")

print(comp_students[:10])

with open('comp_students.txt', 'w') as f:
    for s in comp_students:
        f.write(f"{s[0]},{s[1]}\n")