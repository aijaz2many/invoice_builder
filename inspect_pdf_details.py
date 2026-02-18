from pypdf import PdfReader

reader = PdfReader("app/storage/1/receipt_fields.pdf")
fields = reader.get_fields()

if fields:
    for name, field in fields.items():
        print(f"Name: {name}, Type: {field.get('/FT', 'Unknown')}, Value: {field.get('/V', 'None')}")
else:
    print("No fields found.")
