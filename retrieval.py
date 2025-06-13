# retrieval.py

import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

# === CẤU HÌNH ===
MODEL_NAME = "AITeamVN/Vietnamese_Embedding"  # Bi-encoder
FAISS_INDEX_PATH = "models/rag_index_aiteamvn.faiss"
METADATA_PATH = "models/rag_metadata_aiteamvn.json"
CROSS_ENCODER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Re-ranker

# === LOAD MÔ HÌNH ===
print("🚀 Đang tải mô hình bi-encoder embedding...")
bi_encoder = SentenceTransformer(MODEL_NAME)

print("🎯 Đang tải mô hình cross-encoder re-ranking...")
cross_encoder = CrossEncoder(CROSS_ENCODER_NAME)

# === LOAD FAISS + METADATA ===
print("📥 Đang load FAISS index và metadata ...")
index = faiss.read_index(FAISS_INDEX_PATH)
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# === TẠO EMBEDDING CHO CÂU HỎI ===
def encode_text(text: str):
    return bi_encoder.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

# === HÀM RE-RANKING ===
def rerank_chunks(question, chunks, top_n=5):
    """
    Dùng Cross-Encoder để đánh giá lại độ phù hợp giữa câu hỏi và các đoạn văn.
    """
    pairs = [(question, chunk["text"]) for chunk in chunks]
    scores = cross_encoder.predict(pairs)

    # Sắp xếp lại theo độ phù hợp giảm dần
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    top_chunks = [item[1]["text"] for item in ranked[:top_n]]
    return top_chunks

# === HÀM TRUY XUẤT + RE-RANK ===
def retrieve_chunks(query: str, top_k: int = 10, rerank_top_n: int = 5):
    """
    Truy xuất các đoạn văn bằng FAISS và re-rank bằng Cross-Encoder.
    """
    query_vec = encode_text(query).reshape(1, -1)
    D, I = index.search(query_vec, top_k)
    
    initial_chunks = []
    for idx in I[0]:
        if idx < len(metadata):
            initial_chunks.append(metadata[idx])
    
    # Re-rank lại
    final_chunks = rerank_chunks(query, initial_chunks, top_n=rerank_top_n)
    return final_chunks
