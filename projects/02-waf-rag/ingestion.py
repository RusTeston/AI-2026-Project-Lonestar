"""
WAF RAG Ingestion Script — run once locally.
Chunks the WAF PDF, generates Titan Embeddings V2, writes embeddings.json to S3.
"""
import json, math, re, sys, time
import boto3
import fitz  # PyMuPDF

# ── Config ──────────────────────────────────────────────────────────
PDF_PATH      = "../../AWS_well_architected-framework.pdf"
S3_BUCKET     = "ai-2026-project-lonestar"
S3_KEY        = "projects/02-waf-rag/embeddings.json"
S3_PDF_KEY    = "projects/02-waf-rag/source.pdf"
REGION        = "us-east-1"
EMBED_MODEL   = "amazon.titan-embed-text-v2:0"
CHUNK_TOKENS  = 400   # target tokens per chunk (~3 chars/token → ~1200 chars)
OVERLAP_CHARS = 150   # overlap between chunks
CHARS_PER_CHUNK = 1200
# ────────────────────────────────────────────────────────────────────

bedrock = boto3.client("bedrock-runtime", region_name=REGION)
s3      = boto3.client("s3", region_name=REGION)


def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    print(f"  Extracted text from {len(pages)} pages")
    return pages


def chunk_pages(pages):
    chunks = []
    buffer = ""
    buffer_page = 1

    for p in pages:
        text = re.sub(r'\s+', ' ', p["text"])
        buffer += " " + text

        while len(buffer) >= CHARS_PER_CHUNK:
            chunk_text = buffer[:CHARS_PER_CHUNK].strip()
            chunks.append({"text": chunk_text, "page": buffer_page})
            buffer = buffer[CHARS_PER_CHUNK - OVERLAP_CHARS:]
            buffer_page = p["page"]

    if buffer.strip():
        chunks.append({"text": buffer.strip(), "page": buffer_page})

    print(f"  Created {len(chunks)} chunks")
    return chunks


def embed_chunk(text):
    resp = bedrock.invoke_model(
        modelId=EMBED_MODEL,
        body=json.dumps({"inputText": text[:8000]}),  # Titan V2 max 8192 tokens
        contentType="application/json",
        accept="application/json"
    )
    return json.loads(resp["body"].read())["embedding"]


def main():
    print("=== WAF RAG Ingestion ===")

    # 1. Upload PDF to S3
    print(f"\n[1/4] Uploading PDF to s3://{S3_BUCKET}/{S3_PDF_KEY}")
    s3.upload_file(PDF_PATH, S3_BUCKET, S3_PDF_KEY)
    print("  Done")

    # 2. Extract text
    print("\n[2/4] Extracting text from PDF...")
    pages = extract_text(PDF_PATH)

    # 3. Chunk
    print("\n[3/4] Chunking text...")
    chunks = chunk_pages(pages)

    # 4. Embed
    print(f"\n[4/4] Generating embeddings for {len(chunks)} chunks...")
    results = []
    for i, chunk in enumerate(chunks):
        if i % 50 == 0:
            print(f"  {i}/{len(chunks)}...")
        embedding = embed_chunk(chunk["text"])
        results.append({
            "id":        i,
            "text":      chunk["text"],
            "page":      chunk["page"],
            "embedding": embedding
        })
        time.sleep(0.05)  # avoid throttling

    # 5. Write to S3
    print(f"\nWriting embeddings.json to s3://{S3_BUCKET}/{S3_KEY}")
    body = json.dumps(results, separators=(",", ":"))
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=body.encode("utf-8"),
        ContentType="application/json"
    )
    size_mb = len(body) / 1_000_000
    print(f"  Done — {len(results)} chunks, {size_mb:.1f} MB")
    print("\n✅ Ingestion complete")


if __name__ == "__main__":
    main()
