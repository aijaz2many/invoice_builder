from pypdf import PdfReader

reader = PdfReader("app/storage/1/receipt_fields.pdf")
fields = reader.get_fields()

if fields:
    for field in fields:
        print(f"Field: {field}")
else:
    print("No fields found in PDF.")
