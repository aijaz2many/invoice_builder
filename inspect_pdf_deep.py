from pypdf import PdfReader

reader = PdfReader("app/storage/1/receipt_fields.pdf")
fields = reader.get_fields()

if fields:
    for name, field in fields.items():
        print(f"Field: {name}")
        for key in field:
            print(f"  {key}: {field[key]}")
else:
    print("No fields found.")
