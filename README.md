# Concentrate rejects empty-password encrypted PDFs that Anthropic accepts

**Summary:** An identical Anthropic Messages API request containing a PDF `document` block
succeeds against `api.anthropic.com` but is rejected by `api.concentrate.ai` when the PDF uses
standard *permissions-only* encryption (empty open password). The same PDF without encryption
succeeds through Concentrate. Concentrate appears to inspect/parse the PDF itself instead of
proxying the `document` block to the provider.

## Why it matters
Adobe Sign (and most e-signature tools) apply exactly this encryption to signed documents:
AES-128 (`/R 4`, `/AESV2`), **empty user password**, owner password that only restricts editing.
Anyone can open them without a password; Anthropic reads them natively. Our Salesforce
contract-extraction service sends signed order forms, so nearly all real requests fail via Concentrate.

## Results (2026-11-17)

| Request | Endpoint | Result |
|---|---|---|
| Encrypted PDF | `api.anthropic.com/v1/messages` | **200** – "Acme Test Corp" |
| Identical body | `api.concentrate.ai/v1/messages` | **400** `PDF is encrypted or password-protected` (request_id `8fb0e0fb-8f56-41fd-845e-554951ef6943`) |
| Same PDF, unencrypted | `api.concentrate.ai/v1/messages` | **200** – "Acme Test Corp" |

Real (customer) PDFs fail the same way, sometimes as
`{"code":"invalid_prompt","message":"Invalid PDF: file could not be parsed"}`
(request_ids `ab9d2b0f-703e-4359-8fa2-b032235b27aa`, `cb5e06ee-8272-4ac7-944c-9c343f674c40`,
`9e32c1bb-4722-4fcf-8ebd-6895e45b66bd`). Pinning the provider (`anthropic/claude-opus-4-8`,
`anthropic/claude-opus-5-5`) makes no difference. Failing responses carry UUID request IDs;
successful ones carry Anthropic `msg_…` IDs, which suggests the request is rejected before forwarding.

## Reproduce
```bash
export ANTHROPIC_API_KEY=...      # direct Anthropic key
export CONCENTRATE_API_KEY=...    # Concentrate key
./run.sh
```

## Files
- `payload-encrypted.json` / `payload-plain.json` – complete request bodies (only the PDF differs)
- `pdfs/acme-encrypted.pdf` / `pdfs/acme-plain.pdf` – the 1 KB dummy test PDFs (no customer data)
- `make_pdfs.py` – regenerates both PDFs (`pip install -r requirements.txt && python make_pdfs.py pdfs/acme`)
- `run.sh` – sends the requests and prints status + response

## Ask
Pass Anthropic `document` blocks through unmodified (or support empty-password encrypted PDFs),
matching Anthropic's own behavior.
