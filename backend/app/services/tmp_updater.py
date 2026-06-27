"""
Rewrite rag_pipeline.py to use SearchService internally.
"""
import sys

target = r"d:\Data\OneDrive\RaviAravind\DocuMind\backend\app\services\rag_pipeline.py"

# We read the existing file, keep everything from line 1, but modify key sections
with open(target, "r", encoding="utf-8-sig") as f:
    original = f.read()

# Strategy: keep the LLM sections, prompt templates, utility functions
# but replace the import block, constants, RetrievedChunk, and retrieval functions

# Split into parts: we'll replace imports, constants, and the retrieval section
lines = original.split("\n")

# Find key markers
import_end = 0
for i, line in enumerate(lines):
    if line.startswith("# ---") and "Constants" in line:
        import_end = i
        break

retrieval_start = 0
for i, line in enumerate(lines):
    if line.startswith("# ---") and "Retrieval" in line:
        retrieval_start = i
        break

rerank_start = 0
for i, line in enumerate(lines):
    if line.startswith("# ---") and "Reranking" in line:
        rerank_start = i
        break

retrieval_end = retrieval_start
# Find where utilities section ends and public pipeline starts
for i in range(retrieval_start + 1, len(lines)):
    if lines[i].startswith("# ---") and "Public" in lines[i]:
        retrieval_end = i
        break

if retrieval_end <= retrieval_start:
    retrieval_end = len(lines)

# print(f"Import end: {import_end}, Retrieval: {retrieval_start}-{retrieval_end}, Total lines: {len(lines)}")
print(f"Import end: {import_end}")
print(f"Retrieval section: lines {retrieval_start+1} to {retrieval_end}")
print(f"Total: {len(lines)} lines")
