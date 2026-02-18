from pypdf import PdfReader

reader = PdfReader("app/storage/1/receipt_fields.pdf")
for i, page in enumerate(reader.pages):
    print(f"Page {i}:")
    if "/Annots" in page:
        print(f"  Has {len(page['/Annots'])} annotations")
        for annot in page["/Annots"]:
            obj = annot.get_object()
            if "/T" in obj:
                print(f"    Field: {obj['/T']}")
    else:
        print("  No annotations")

if "/AcroForm" in reader.trailer["/Root"]:
    acro = reader.trailer["/Root"]["/AcroForm"]
    if "/Fields" in acro:
        print(f"AcroForm has {len(acro['/Fields'])} fields")
