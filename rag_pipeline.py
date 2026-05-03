"""
RAG Pipeline for Placement Prep Assistant
Handles data loading, chunking, embedding generation, vector storage, and retrieval

Retrieval Quality Improvements:
  - chunk_size=400, chunk_overlap=80  → focused, complete-idea chunks
  - k=5 retrieval                     → wider coverage per query
  - Full-content SHA-256 deduplication → no near-duplicate chunks
  - Numbered context sources          → clean, structured LLM input
  - Debug logging                     → visible retrieval trace
  - Tavily web-search                 → real-time learning links per query
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

# ── Tavily web-search helper (fails silently if key missing) ───────────────────
from tavily_search import get_useful_links

# ── Retrieval debug logger ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[RAG] %(levelname)s | %(message)s",
)
logger = logging.getLogger("rag_pipeline")


class RAGPipeline:
    """
    RAG Pipeline for answering questions based on custom knowledge base
    Uses HuggingFace local embeddings and Groq LLM, FAISS for vector storage
    """

    def __init__(self, groq_api_key: str, data_folder: str = "data", vector_store_path: str = "vector_store"):
        """
        Initialize RAG Pipeline
        
        Args:
            groq_api_key: Groq API key (for LLM)
            data_folder: Path to folder containing data files
            vector_store_path: Path to save/load FAISS vector store
        """
        self.groq_api_key = groq_api_key
        self.data_folder = data_folder
        self.vector_store_path = vector_store_path
        self.vector_store = None
        self.retriever = None
        self.rag_chain = None      # used when context is relevant
        self.general_chain = None  # used when context is weak/missing

        # Similarity thresholds (FAISS L2 distance — lower = more similar)
        self.RAG_THRESHOLD = 0.8       # strong match  → pure RAG
        self.HYBRID_THRESHOLD = 1.3    # partial match → hybrid (RAG + general knowledge)
        # above HYBRID_THRESHOLD     → pure general knowledge

        # Initialize local embeddings (no API key needed)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        # LLM for grounded RAG answers
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_api_key,
            temperature=0.4   # lower = more faithful to context
        )

        # LLM for general-knowledge answers (slightly more creative)
        self.llm_general = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_api_key,
            temperature=0.7
        )

    def load_documents_from_folder(self) -> List[Document]:
        """
        Load all text files from the data folder and convert to Document objects
        
        Returns:
            List of Document objects with content and metadata
        """
        documents = []
        
        if not os.path.exists(self.data_folder):
            print(f"Error: Data folder '{self.data_folder}' not found!")
            return documents
        
        # Iterate through all text files in data folder
        for filename in os.listdir(self.data_folder):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.data_folder, filename)
                print(f"Loading: {filename}")
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Create Document with metadata
                doc = Document(
                    page_content=content,
                    metadata={"source": filename}
                )
                documents.append(doc)
        
        print(f"\nTotal documents loaded: {len(documents)}")
        return documents

    def split_documents(
        self,
        documents: List[Document],
        chunk_size: int = 400,
        chunk_overlap: int = 80,
    ) -> List[Document]:
        """
        Split documents into focused, complete-idea chunks for high-quality retrieval.

        Args:
            documents:     List of Document objects
            chunk_size:    Target character length per chunk (300-500 is optimal for
                           sentence-level semantic completeness)
            chunk_overlap: Overlap between consecutive chunks so no idea is cut off
                           at a boundary

        Returns:
            List of chunked Document objects
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            # Prefer splitting at paragraph/sentence boundaries to keep ideas intact
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
            length_function=len,
        )

        chunks = []
        for doc in documents:
            split_docs = splitter.split_documents([doc])
            # Filter out very short chunks that won't carry meaningful semantics
            meaningful = [c for c in split_docs if len(c.page_content.strip()) >= 80]
            chunks.extend(meaningful)

        logger.info("Total meaningful chunks created: %d", len(chunks))

        # ── Debug: log first chunk from each source ───────────────────────────
        seen_sources: set = set()
        for chunk in chunks:
            src = chunk.metadata.get("source", "unknown")
            if src not in seen_sources:
                seen_sources.add(src)
                preview = chunk.page_content[:120].replace("\n", " ")
                logger.info("  Sample chunk [%s]: %s…", src, preview)

        return chunks

    def create_vector_store(self, documents: List[Document], rebuild: bool = False) -> FAISS:
        """
        Create FAISS vector store from documents
        
        Args:
            documents: List of Document objects
            rebuild: If True, rebuild vector store; if False, load existing
            
        Returns:
            FAISS vector store object
        """
        vector_store_file = os.path.join(self.vector_store_path, "faiss_index")
        
        # Check if vector store already exists and rebuild is False
        if os.path.exists(vector_store_file) and not rebuild:
            print(f"Loading existing FAISS index from {vector_store_file}")
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                index_name="faiss_index",
                allow_dangerous_deserialization=True
            )
        else:
            print("Creating new FAISS vector store...")
            if not documents:
                raise ValueError("No documents provided to create vector store")
            
            # Create vector store from documents
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
            # Save vector store
            os.makedirs(self.vector_store_path, exist_ok=True)
            self.vector_store.save_local(
                self.vector_store_path,
                index_name="faiss_index"
            )
            print(f"Vector store saved to {self.vector_store_path}")
        
        return self.vector_store

    def setup_retriever(self, k: int = 5) -> None:
        """
        Setup retriever to fetch top-k relevant chunks.
        k=5 provides wider coverage so important definitions are not missed.

        Args:
            k: Number of top relevant chunks to retrieve (default 5)
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")

        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        logger.info("Retriever configured with k=%d", k)

    def check_embedding_quality(self, test_texts: List[str] = None) -> None:
        """
        Sanity-check that embeddings are non-zero and have correct dimensionality.
        Logs a warning if any embedding looks degenerate.
        """
        if test_texts is None:
            test_texts = ["What is overfitting?", "Explain normalization in DBMS"]
        try:
            vecs = self.embeddings.embed_documents(test_texts)
            for text, vec in zip(test_texts, vecs):
                norm = sum(x ** 2 for x in vec) ** 0.5
                logger.info(
                    "Embedding check | text='%s…' | dim=%d | norm=%.4f",
                    text[:40], len(vec), norm,
                )
                if norm < 1e-6:
                    logger.warning("⚠ Near-zero embedding detected for: '%s'", text)
        except Exception as exc:
            logger.error("Embedding quality check failed: %s", exc)

    def create_qa_chain(self) -> None:
        """
        Creates two chains using ChatPromptTemplate (system + human roles).
        Context is injected silently into the system role — the model never
        sees it labeled as 'notes', 'context', or 'documents', so it cannot
        reference them in its output.
        """
        if self.retriever is None:
            raise ValueError("Retriever not initialized. Call setup_retriever() first.")

        ANSWER_FORMAT = """Structure your answer using these sections (use only what applies):
**Definition:** One crisp, clear sentence.
**Explanation:** 2–4 sentences with depth and reasoning.
**Example:** A short real-world or code example.
**Interview Tip:** One practical tip for job interviews."""

        # ── Chain 1: RAG  ─────────────────────────────────────────────────────
        # Context goes into the SYSTEM message as the assistant's own knowledge.
        # The human message is ONLY the question — no mention of sources ever.
        rag_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a knowledgeable placement preparation assistant.\n\n"
             "{context}\n\n"  # silently injected — no label, no header
             "Answer the user's question clearly and confidently.\n"
             "NEVER mention notes, context, documents, sources, or study material.\n"
             "NEVER say phrases like 'based on the above', 'as mentioned', "
             "'the information states', 'the material covers', or any similar phrase.\n"
             "Speak as a confident teacher who simply knows the answer.\n\n"
             + ANSWER_FORMAT),
            ("human", "{question}"),
        ])

        # ── Chain 2: General  ─────────────────────────────────────────────────
        # Pure LLM — no context injected at all.
        general_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a knowledgeable placement preparation assistant.\n"
             "Answer the user's question clearly, confidently, and in an interview-ready style.\n"
             "Do NOT add disclaimers. Do NOT say you don't have information unless "
             "the topic is completely unknown to you.\n\n"
             + ANSWER_FORMAT),
            ("human", "{question}"),
        ])

        self.rag_chain     = rag_prompt     | self.llm         | StrOutputParser()
        self.general_chain = general_prompt | self.llm_general | StrOutputParser()
        self.qa_chain = self.rag_chain  # backwards-compat alias
        print("QA chains created successfully (RAG + General + Hybrid Router)")

    def query(self, question: str) -> Tuple[str, List[dict], List[dict]]:
        """
        Hybrid query: routes to RAG, HYBRID, or GENERAL mode based on
        FAISS similarity scores so the assistant never unnecessarily fails.
        Also fetches real-time learning links via Tavily (third return value).

        Routing logic (FAISS L2 distance — lower = more similar):
          score <= RAG_THRESHOLD     → pure RAG (strong context match)
          score <= HYBRID_THRESHOLD  → hybrid (context + general knowledge)
          score >  HYBRID_THRESHOLD  → pure general knowledge (LLM only)
        """
        import re

        if self.rag_chain is None or self.general_chain is None:
            raise ValueError("Chains not initialized. Call create_qa_chain() first.")

        logger.info("="*60)
        logger.info("QUERY: %s", question)
        logger.info("="*60)

        # ── Step 1: Scored retrieval (k=5 for wider coverage) ─────────────────
        scored_docs = self.vector_store.similarity_search_with_score(question, k=5)
        logger.info("Retrieved %d raw docs from FAISS", len(scored_docs))

        # ── Step 2: Deduplicate using full-content SHA-256 hash ───────────────
        # Using full content hash prevents near-duplicate chunks from polluting
        # the context (e.g., two chunks with almost the same text but different
        # first 120 chars).
        seen_hashes: set = set()
        unique_scored: List[Tuple[Document, float]] = []
        for doc, score in scored_docs:
            content_hash = hashlib.sha256(
                doc.page_content.strip().encode("utf-8")
            ).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_scored.append((doc, score))

        logger.info("After deduplication: %d unique docs", len(unique_scored))

        # ── Step 3: Debug — log each retrieved chunk ──────────────────────────
        for rank, (doc, score) in enumerate(unique_scored, start=1):
            preview = doc.page_content.strip()[:150].replace("\n", " ")
            logger.info(
                "  [Rank %d] score=%.4f | source=%s | preview: %s…",
                rank,
                score,
                doc.metadata.get("source", "unknown"),
                preview,
            )

        # ── Step 4: Determine routing mode ────────────────────────────────────
        best_score = unique_scored[0][1] if unique_scored else float("inf")
        relevant   = [(d, s) for d, s in unique_scored if s <= self.HYBRID_THRESHOLD]

        if best_score <= self.RAG_THRESHOLD:
            mode = "rag"
        elif best_score <= self.HYBRID_THRESHOLD:
            mode = "hybrid"
        else:
            mode = "general"

        logger.info(
            "[Router] best_score=%.4f | relevant_chunks=%d | mode=%s",
            best_score, len(relevant), mode.upper(),
        )

        # ── Step 5: Build clean, numbered context string ──────────────────────
        # Numbered sources help the LLM distinguish between different chunks
        # and reduces hallucination by grounding answers to specific passages.
        if mode in ("rag", "hybrid") and relevant:
            context_parts = [
                f"Source {i}:\n{doc.page_content.strip()}"
                for i, (doc, _) in enumerate(relevant, start=1)
            ]
            context_str = "\n\n".join(context_parts)
            logger.info("Context built from %d source(s) (%d chars)",
                        len(context_parts), len(context_str))
        else:
            context_str = ""
            logger.info("No relevant context — switching to general knowledge mode")

        # ── Step 6: Generate answer ────────────────────────────────────────────
        if mode == "general" or not context_str:
            answer = self.general_chain.invoke({"question": question})
        else:
            answer = self.rag_chain.invoke({"context": context_str, "question": question})

        # ── Step 7: Post-processing — strip any slipped meta-phrases ──────────
        META_PHRASES = [
            "the notes", "my notes", "the context", "based on the",
            "according to the", "the provided", "background knowledge",
            "the information provided", "provided information",
            "does not cover", "not covered", "not mentioned",
            "the document", "the material",
        ]

        sentences = re.split(r'(?<=[.!?])\s+', answer)
        clean_sentences = [
            s for s in sentences
            if not any(p in s.lower() for p in META_PHRASES)
        ]
        answer = " ".join(clean_sentences).strip() or answer

        # ── Step 8: Format source metadata for UI ─────────────────────────────
        sources = []
        for doc, score in unique_scored[:5]:  # show up to top-5 in UI
            snippet = doc.page_content.strip()
            sources.append({
                "source": doc.metadata.get("source", "Unknown"),
                "content": snippet[:300] + "\u2026" if len(snippet) > 300 else snippet,
                "score": round(score, 4),
                "mode": mode,
            })

        logger.info("Answer generated (%d chars) | mode=%s", len(answer), mode)

        # ── Step 9: Fetch real-time learning links (Tavily) ───────────────────
        # Called AFTER answer generation so a slow network never delays the LLM.
        # get_useful_links() always returns [] on error — app is never broken.
        links = get_useful_links(question)
        logger.info("Tavily links fetched: %d", len(links))

        return answer, sources, links

    def initialize(self, rebuild_vector_store: bool = False) -> None:
        """
        Complete initialization pipeline
        Loads data, chunks it, creates vector store, and sets up QA chain
        
        Args:
            rebuild_vector_store: If True, rebuild the vector store from scratch
        """
        print("=" * 50)
        print("Initializing RAG Pipeline")
        print("=" * 50)
        
        # Step 1: Load documents
        documents = self.load_documents_from_folder()
        
        if not documents:
            print("Warning: No documents loaded!")
            return
        
        # Step 2: Split documents with optimized chunking parameters
        # chunk_size=400: captures a complete idea without being too long
        # chunk_overlap=80: ~20% overlap prevents idea truncation at boundaries
        chunks = self.split_documents(documents, chunk_size=400, chunk_overlap=80)

        # Step 3: Create vector store
        self.create_vector_store(chunks, rebuild=rebuild_vector_store)

        # Step 4: Sanity-check embedding quality
        self.check_embedding_quality()

        # Step 5: Setup retriever with k=5 for wider coverage
        self.setup_retriever(k=5)

        # Step 6: Create QA chain
        self.create_qa_chain()

        logger.info("=" * 50)
        logger.info("RAG Pipeline initialized successfully!")
        logger.info("=" * 50)


# Example usage and test queries
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    GROQ_KEY = os.getenv("GROQ_API_KEY")
    
    if not GROQ_KEY:
        print("Error: GROQ_API_KEY not found in environment variables")
        print("Please set your Groq API key in .env file")
    else:
        # Initialize RAG pipeline
        rag = RAGPipeline(groq_api_key=GROQ_KEY)
        rag.initialize()
        
        # Example queries
        example_queries = [
            "What is overfitting in machine learning?",
            "Explain the concept of normalization in DBMS",
            "What is a stack data structure?",
            "What is the bias-variance tradeoff?",
            "Tell me about AVL trees"
        ]
        
        print("\n" + "=" * 50)
        print("Testing RAG System with Example Queries")
        print("=" * 50)
        
        for query in example_queries:
            print(f"\nQuestion: {query}")
            print("-" * 50)
            answer, sources = rag.query(query)
            print(f"Answer: {answer}")
            print(f"\nSources used: {len(sources)}")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {source['source']}")
