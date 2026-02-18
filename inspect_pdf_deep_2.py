from pypdf import PdfReader

reader = PdfReader("app/storage/1/receipt_fields.pdf")
# Get fields directly from the first page's annotations
page = reader.pages[0]
if "/Annots" in page:
    for annot in page["/Annots"]:
        obj = annot.get_object()
        if "/T" in obj:
            print(f"Field Name (/T): {obj['/T']}")
            if "/DA" in obj:
                print(f"  DA: {obj['/DA']}")
            else:
                print("  No DA (Default Appearance)")
