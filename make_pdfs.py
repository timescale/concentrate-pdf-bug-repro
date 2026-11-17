import sys, pikepdf
from pikepdf import Pdf, Dictionary, Name, Array, Encryption, Permissions
out = sys.argv[1]
pdf = Pdf.new()
font = pdf.make_indirect(Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name.Helvetica))
content = b"BT /F1 18 Tf 72 720 Td (Test Order Form) Tj 0 -30 Td /F1 12 Tf (Customer: Acme Test Corp) Tj 0 -20 Td (Term: 12 months) Tj ET"
page = Dictionary(Type=Name.Page, MediaBox=Array([0,0,612,792]),
                  Resources=Dictionary(Font=Dictionary(F1=font)),
                  Contents=pdf.make_stream(content))
pdf.pages.append(pikepdf.Page(page))
pdf.save(out + "-plain.pdf")
# Mimic Adobe Sign: AES-128 (R4/AESV2), EMPTY user password, owner password, editing disallowed
pdf.save(out + "-encrypted.pdf", encryption=Encryption(owner="owner-secret", user="", R=4, aes=True,
         allow=Permissions(modify_annotation=False, modify_assembly=False, modify_form=False, modify_other=False)))
for f in ("-plain.pdf", "-encrypted.pdf"):
    p = Pdf.open(out + f)  # opens with empty password
    print(f, "encrypted:", p.is_encrypted, "| text ok:", b"Acme" in p.pages[0].Contents.read_bytes())
