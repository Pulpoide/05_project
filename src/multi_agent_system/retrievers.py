"""Retrievers for domain-specific RAG agents.

This file intentionally provides a simple keyword retriever as a placeholder.
Replace it with embeddings + vector DB for production.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# STOPWORDS = {
#     "de",
#     "la",
#     "el",
#     "y",
#     "en",
#     "a",
#     "que",
#     "como",
#     "con",
#     "para",
#     "por",
#     "un",
#     "una",
# }


# def _tokens(text: str) -> list[str]:
#     text = text.lower().replace("/", " ").replace(",", " ").replace(".", " ")
#     return [t for t in text.split() if t and t not in STOPWORDS and len(t) > 2]


# class SimpleKeywordRetriever(BaseRetriever):
#     """Small baseline retriever based on token overlap.

#     TODO (production): replace with semantic retriever backed by embeddings.
#     """

#     docs: list[Document]
#     k: int = 4

#     def _get_relevant_documents(
#         self,
#         query: str,
#         *,
#         run_manager: CallbackManagerForRetrieverRun,
#     ) -> list[Document]:
#         query_tokens = _tokens(query)
#         token_set = set(query_tokens)

#         def score(doc: Document) -> int:
#             content_lower = doc.page_content.lower()
#             overlap = sum(1 for token in token_set if token in content_lower)
#             phrase_bonus = 0
#             for token in query_tokens:
#                 if token in content_lower:
#                     phrase_bonus += 1
#             return overlap * 2 + phrase_bonus

#         ranked = sorted(self.docs, key=score, reverse=True)
#         best = ranked[: self.k]
#         if not best:
#             return []

#         scored_docs: list[Document] = []
#         for doc in best:
#             value = score(doc)
#             scored_docs.append(
#                 Document(
#                     page_content=doc.page_content,
#                     metadata={**doc.metadata, "keyword_score": value},
#                 )
#             )
#         return scored_docs


# def _split_markdown_to_docs(text: str, source: str) -> list[Document]:
#     chunks = [chunk.strip() for chunk in text.split("\n- ") if chunk.strip()]
#     docs = []
#     for idx, chunk in enumerate(chunks, start=1):
#         docs.append(
#             Document(page_content=chunk, metadata={"source": source, "chunk_id": idx})
#         )
#     return docs


# def load_domain_docs(markdown_paths: Iterable[Path]) -> list[Document]:
#     docs: list[Document] = []
#     for path in markdown_paths:
#         if not path.exists():
#             continue
#         content = path.read_text(encoding="utf-8")
#         docs.extend(_split_markdown_to_docs(content, source=str(path.name)))
#     return docs


# def build_hr_retriever(project_root: Path) -> BaseRetriever:
#     docs = load_domain_docs([project_root / "data" / "hr" / "manual_rrhh.md"])
#     return SimpleKeywordRetriever(docs=docs, k=4)


# def build_tech_retriever(project_root: Path) -> BaseRetriever:
#     docs = load_domain_docs([project_root / "data" / "tech" / "runbook_tech.md"])
#     return SimpleKeywordRetriever(docs=docs, k=4)


def _get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def _split_markdown_to_docs(text: str, source: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n- ", "\n\n", " ", ""],
    )
    return splitter.create_documents([text], metadatas=[{"source": source}])


def load_domain_docs(markdown_paths: Iterable[Path]) -> list[Document]:
    docs: list[Document] = []
    for path in markdown_paths:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        docs.extend(_split_markdown_to_docs(content, source=str(path.name)))
    return docs


def build_semantic_retriever(markdown_file: Path) -> BaseRetriever:
    """Crea un retriever semántico basado en un archivo específico."""
    docs = load_domain_docs([markdown_file])

    # Creamos la base de datos vectorial en memoria (ephemeral)
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=_get_embeddings(),
        collection_name=f"split_{markdown_file.stem}",
    )

    # k=4 significa que traerá los 4 fragmentos más parecidos
    return vectorstore.as_retriever(search_kwargs={"k": 4})


# --- Constructores finales ---
def build_hr_retriever(project_root: Path) -> BaseRetriever:
    path = project_root / "data" / "hr" / "manual_rrhh.md"
    return build_semantic_retriever(path)


def build_tech_retriever(project_root: Path) -> BaseRetriever:
    path = project_root / "data" / "tech" / "runbook_tech.md"
    return build_semantic_retriever(path)
