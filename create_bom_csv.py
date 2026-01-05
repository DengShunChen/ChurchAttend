
import csv

content = [
    {"Name": "BOMTest1", "Phone": "0933333333", "Group": "TestGroup"},
    {"Name": "BOMTest2", "Phone": "0944444444", "Group": "TestGroup"}
]

# Write with utf-8-sig to include BOM
with open('test_import_bom.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Phone", "Group"])
    writer.writeheader()
    writer.writerows(content)

print("Created test_import_bom.csv with BOM")
