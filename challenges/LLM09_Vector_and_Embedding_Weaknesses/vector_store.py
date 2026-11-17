from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

current_folder = os.getcwd()
model = SentenceTransformer("paraphrase-MiniLM-L3-v2", cache_folder=current_folder)
index = faiss.IndexFlatL2(model.get_sentence_embedding_dimension())

doc_map = {}
doc_count = 0

def search_similar(query, k=2):
    if doc_count == 0:
        return []

    q_vec = model.encode([query])
    D, I = index.search(np.array(q_vec), k)

    # Filter out -1 and non-existent keys
    results = []
    for idx in I[0]:
        if idx in doc_map:
            results.append(doc_map[idx])

    return results

def add_document(text):
    global doc_count
    vec = model.encode([text])
    index.add(np.array(vec))
    doc_map[doc_count] = text
    doc_count += 1

def clear_vector_store():
    global index, doc_map, doc_count
    # Re-initialize the index and document map
    index = faiss.IndexFlatL2(model.get_sentence_embedding_dimension())
    doc_map.clear()
    doc_count = 0
