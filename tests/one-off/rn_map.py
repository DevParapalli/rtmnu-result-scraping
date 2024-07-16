old_start = int(input("Enter OLD Starting:"))
old_end = int(input("Enter OLD Ending:"))
old_known = int(input("Enter OLD Known:"))
new_known = int(input("Enter NEW Known:"))
offset = new_known - old_known
new_start = old_start + offset
new_end = old_end + offset

while True:
    old = int(input("OLD:"))
    if old == 0:
        break
    new = old + offset
    print(f"NEW: {new}")
