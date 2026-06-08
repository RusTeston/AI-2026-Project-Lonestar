"""
WAF RAG Query Handler
Loads embeddings from S3 on cold start, performs cosine similarity,
calls Bedrock Nova Lite via Converse API with top-k context chunks.
"""
import json, math, os, boto3

BUCKET       = os.environ["EMBEDDINGS_BUCKET"]
KEY          = os.environ["EMBEDDINGS_KEY"]
EMBED_MODEL  = "amazon.titan-embed-text-v2:0"
GEN_MODEL    = "us.amazon.nova-lite-v1:0"
TOP_K        = 5
REGION       = "us-east-1"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)
s3      = boto3.client("s3", region_name=REGION)

# Module-level cache — persists across warm invocations
_embeddings = None

CORS = {
    "Access-Control-Allow-Origin":  "https://ai.rus-teston.com",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}

SYSTEM_PROMPT = """You are an AWS Well-Architected Framework expert assistant.
Answer the user's question using ONLY the context provided below.
If the context does not contain enough information to answer fully, say so clearly.
Always cite the page numbers from the context in your answer.
Be concise and specific."""


def load_embeddings():
    global _embeddings
    if _embeddings is None:
        print("Cold start — loading embeddings from S3...")
        obj = s3.get_object(Bucket=BUCKET, Key=KEY)
        _embeddings = json.loads(obj["Body"].read())
        print(f"Loaded {len(_embeddings)} chunks")
    return _embeddings


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def embed_query(text):
    resp = bedrock.invoke_model(
        modelId=EMBED_MODEL,
        body=json.dumps({"inputText": text[:8000]}),
        contentType="application/json",
        accept="application/json"
    )
    return json.loads(resp["body"].read())["embedding"]


def retrieve_top_k(query_embedding, chunks, k=TOP_K):
    scored = [
        (cosine_similarity(query_embedding, c["embedding"]), c)
        for c in chunks
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


def generate_answer(question, top_chunks):
    context_parts = []
    for score, chunk in top_chunks:
        context_parts.append(f"[Page {chunk['page']}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_parts)

    user_message = f"Context from the AWS Well-Architected Framework:\n\n{context}\n\nQuestion: {question}"

    resp = bedrock.converse(
        modelId=GEN_MODEL,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": user_message}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0.1}
    )
    answer = resp["output"]["message"]["content"][0]["text"]
    sources = sorted(set(chunk["page"] for _, chunk in top_chunks))
    return answer, sources


def respond(status, body):
    return {"statusCode": status, "headers": CORS, "body": json.dumps(body)}


def handler(event, context):
    if event.get("httpMethod") == "OPTIONS" or event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return respond(200, {})

    try:
        body = json.loads(event.get("body") or "{}")
        question = (body.get("question") or "").strip()
        if not question:
            return respond(400, {"error": "question is required"})
        if len(question) > 1000:
            return respond(400, {"error": "question too long (max 1000 chars)"})

        chunks = load_embeddings()
        query_embedding = embed_query(question)
        top_chunks = retrieve_top_k(query_embedding, chunks)
        answer, sources = generate_answer(question, top_chunks)

        return respond(200, {"answer": answer, "sources": sources})

    except Exception as e:
        print(f"Error: {e}")
        return respond(500, {"error": "Internal server error"})
