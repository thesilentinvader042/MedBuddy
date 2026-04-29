import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()

from models import QueryRequest, DiagnosticResponse
from pipeline.preprocessor import normalize
from pipeline.intent import classify_intent
from pipeline.decomposer import decompose
from pipeline.retriever import hybrid_retrieve, build_bm25_index, get_collection
from pipeline.validator import validate_and_rerank
from pipeline.compressor import compress_context
from pipeline.binder import bind_evidence
from pipeline.generator import generate
from pipeline.formatter import format_output
from pipeline.scorer import score_confidence
from pipeline.gate import gate_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    col = get_collection()
    if col.count() == 0:
        print("⚠️  Empty store detected — running auto-seed...")
        import subprocess
        subprocess.run(["python", "data/seed_docs.py"])
        print("✅ Auto-seed complete")
    build_bm25_index()
    print("✅ Vector store and BM25 index ready")

    yield  # app runs here

    # ── Shutdown ─────────────────────────────────────────────
    print("🛑 Shutting down MedQA")


app = FastAPI(title="MedQA API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def run_pipeline(req: QueryRequest) -> DiagnosticResponse:

    # Stage 2 — Preprocess
    normalized, entities = normalize(req.query)

    # Stage 3 — Intent classification
    intent_result = await classify_intent(normalized)
    intent = intent_result["intent"]
    intent_confidence = intent_result["confidence"]

    # Stage 4 — Query decomposition
    sub_queries = await decompose(normalized, entities, req.age)

    # Stage 5 — Hybrid RAG retrieval
    raw_chunks = await hybrid_retrieve(sub_queries, top_k=7)

    # Stage 6 — Validate and rerank
    validated_chunks = validate_and_rerank(raw_chunks)

    # Early gate — no evidence at all
    if not validated_chunks:
        return DiagnosticResponse(
            answer="",
            key_points=[],
            citations=[],
            confidence="low",
            intent=intent,
            disclaimer="For informational purposes only. Not a substitute for professional medical advice.",
            fallback=True,
            fallback_reason="No relevant evidence found in trusted sources for this query.",
        )

    # Stage 7 — Compress context
    compressed = compress_context(validated_chunks)

    # Stage 8 — Bind evidence
    citations = bind_evidence(validated_chunks)

    # Stage 9 — Generate
    patient_info = ""
    if req.age:
        patient_info += f"Age: {req.age}"
    if req.sex:
        patient_info += f", Sex: {req.sex}"
    if req.context:
        patient_info += f", Context: {req.context}"

    raw_answer = await generate(
        query=normalized,
        compressed_context=compressed,
        intent=intent,
        patient_info=patient_info,
        evidence_chunks=validated_chunks,
    )

    # Stage 10 — Format output
    answer, key_points = format_output(raw_answer)

    # Stage 11 — Confidence scoring
    confidence = score_confidence(validated_chunks, intent_confidence, answer)

    # Stage 12 — Failure gate
    gate = gate_check(confidence, validated_chunks, intent)
    if not gate["pass"]:
        return DiagnosticResponse(
            answer="",
            key_points=[],
            citations=citations,
            confidence=confidence,
            intent=intent,
            disclaimer="For informational purposes only. Not a substitute for professional medical advice.",
            fallback=True,
            fallback_reason=gate["reason"],
        )

    return DiagnosticResponse(
        answer=answer,
        key_points=key_points,
        citations=citations,
        confidence=confidence,
        intent=intent,
        disclaimer="For informational purposes only. Not a substitute for professional medical advice, diagnosis, or treatment.",
        fallback=False,
    )


@app.post("/api/query", response_model=DiagnosticResponse)
async def query(req: QueryRequest):
    try:
        return await run_pipeline(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    col = get_collection()
    return {
        "status": "ok",
        "docs_in_store": col.count(),
        "model": os.getenv("GROQ_MODEL"),
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")