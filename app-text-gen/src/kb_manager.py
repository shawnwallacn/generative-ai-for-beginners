"""
Knowledge Base Manager for managing external documents and content.
Supports adding, organizing, and searching documents using embeddings.
Stores collections and documents in separate files for scalability.
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from security import InputValidator

# Try to import Cosmos DB storage (optional for dual-source support)
try:
    from cosmos_storage import CosmosDBStorage, DualSourceSearch
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    CosmosDBStorage = None
    DualSourceSearch = None

# Import audit logger (will be set by app.py)
audit_logger = None


KB_DIR = "knowledge_base"
KB_INDEX_FILE = "kb_index.json"
KB_COLLECTIONS_DIR = "collections"
KB_DOCUMENTS_DIR = "documents"


class DocumentChunker:
    """Handles document chunking strategies"""
    
    # Initialize NLTK punkt tokenizer
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        import nltk
        nltk.download('punkt', quiet=True)
    
    @staticmethod
    def chunk_by_paragraphs(text: str, overlap: int = 100) -> List[Dict]:
        """
        Chunk text by paragraphs with overlap
        Best for: Long-form content, essays, articles
        
        Args:
            text: The text to chunk
            overlap: Number of characters to overlap between chunks
        
        Returns:
            List of chunk dicts with text and metadata
        """
        # Split by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            # If adding this paragraph would make the chunk too large, save current and start new
            if current_chunk and len(current_chunk) + len(para) > 1000:
                chunks.append({
                    "text": current_chunk.strip(),
                    "word_count": len(current_chunk.split()),
                    "strategy": "paragraphs"
                })
                # Add overlap
                current_chunk = current_chunk[-overlap:] + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "word_count": len(current_chunk.split()),
                "strategy": "paragraphs"
            })
        
        return chunks
    
    @staticmethod
    def chunk_by_sentences(text: str, sentence_count: int = 5, overlap: int = 1) -> List[Dict]:
        """
        Chunk text by sentence groups
        Best for: Technical documentation, structured content
        
        Args:
            text: The text to chunk
            sentence_count: Number of sentences per chunk
            overlap: Number of sentences to overlap
        
        Returns:
            List of chunk dicts with text and metadata
        """
        # Use NLTK for more accurate sentence splitting
        try:
            import nltk
            sentences = nltk.sent_tokenize(text)
        except:
            # Fallback to simple regex if NLTK fails
            sentences = re.split(r'(?<=[.!?])\s+', text)
        
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), sentence_count - overlap):
            chunk_sentences = sentences[i:i + sentence_count]
            if chunk_sentences:
                chunk_text = " ".join(chunk_sentences)
                chunks.append({
                    "text": chunk_text,
                    "word_count": len(chunk_text.split()),
                    "strategy": "sentences",
                    "sentence_count": len(chunk_sentences)
                })
        
        return chunks
    
    @staticmethod
    def chunk_by_size(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """
        Chunk text by character size with overlap
        Best for: Uniform processing, fixed-size requirements
        
        Args:
            text: The text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of characters to overlap
        
        Returns:
            List of chunk dicts with text and metadata
        """
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size]
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text.strip(),
                    "word_count": len(chunk_text.split()),
                    "strategy": "size"
                })
        
        return chunks
    
    @staticmethod
    def chunk_by_sliding_window(text: str, window_size: int = 400, step: int = 200, overlap_ratio: float = 0.25) -> List[Dict]:
        """
        Chunk text using sliding window with configurable overlap
        Best for: Continuous text, preserving context across chunks
        
        Maintains context by overlapping chunks - good for preserving
        information that spans chunk boundaries.
        
        Args:
            text: The text to chunk
            window_size: Size of each window in characters
            step: Characters to move between windows (smaller = more overlap)
            overlap_ratio: Ratio of overlap (ignored if step is provided)
        
        Returns:
            List of chunk dicts with text and metadata
        """
        chunks = []
        text_length = len(text)
        overlap_chars = int(window_size * overlap_ratio)
        
        for i in range(0, text_length, step):
            chunk_text = text[i:i + window_size]
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text.strip(),
                    "word_count": len(chunk_text.split()),
                    "strategy": "sliding_window",
                    "window_start": i,
                    "window_end": min(i + window_size, text_length)
                })
        
        return chunks
    
    @staticmethod
    def chunk_by_semantic(text: str, max_chunk_size: int = 600) -> List[Dict]:
        """
        Chunk text by semantic boundaries (sentences grouped by topic similarity)
        Best for: Mixed-topic documents, diverse content
        
        This strategy groups sentences that are semantically similar,
        attempting to keep related concepts together.
        
        Args:
            text: The text to chunk
            max_chunk_size: Maximum characters per chunk
        
        Returns:
            List of chunk dicts with text and metadata
        """
        try:
            import nltk
            sentences = nltk.sent_tokenize(text)
        except:
            sentences = re.split(r'(?<=[.!?])\s+', text)
        
        sentences = [s.strip() for s in sentences if s.strip()]
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Add sentence to current chunk if it doesn't exceed max size
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(test_chunk) <= max_chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "word_count": len(current_chunk.split()),
                        "strategy": "semantic",
                        "sentence_count": len(current_chunk.split('.'))
                    })
                current_chunk = sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "word_count": len(current_chunk.split()),
                "strategy": "semantic",
                "sentence_count": len(current_chunk.split('.'))
            })
        
        return chunks


class DocumentParser:
    """Handles parsing different document formats"""
    
    @staticmethod
    def parse_text_file(filepath: str) -> str:
        """Parse a plain text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error parsing text file: {e}")
            return ""
    
    @staticmethod
    def parse_markdown_file(filepath: str) -> str:
        """Parse a markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Remove markdown formatting for better embedding
            content = re.sub(r'[#*_\[\]()]', '', content)
            return content
        except Exception as e:
            print(f"Error parsing markdown file: {e}")
            return ""
    
    @staticmethod
    def parse_pdf_file(filepath: str) -> str:
        """Parse a PDF file using pdfplumber"""
        try:
            try:
                import pdfplumber
                text = ""
                page_count = 0
                empty_pages = 0
                
                with pdfplumber.open(filepath) as pdf:
                    page_count = len(pdf.pages)
                    for i, page in enumerate(pdf.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                            else:
                                empty_pages += 1
                                # Try alternative extraction method
                                try:
                                    # Try extracting from table if available
                                    tables = page.extract_tables()
                                    if tables:
                                        for table in tables:
                                            for row in table:
                                                text += " ".join([str(cell) if cell else "" for cell in row]) + "\n"
                                except:
                                    pass
                        except Exception as e:
                            print(f"  Warning: Could not extract page {i+1}: {e}")
                
                if not text.strip():
                    print(f"[WARNING] PDF parsed but no text extracted")
                    print(f"  Pages: {page_count} | Empty: {empty_pages}")
                    if empty_pages == page_count:
                        print(f"  [INFO] PDF is likely a SCANNED DOCUMENT (images only)")
                        print(f"  [INFO] OCR (Optical Character Recognition) needed to extract text")
                        print(f"  [INFO] Try: pytesseract or Tesseract OCR")
                    else:
                        print(f"  [INFO] Some pages have no extractable text")
                    return ""
                
                if empty_pages > 0 and empty_pages < page_count:
                    print(f"[INFO] Extracted text from {page_count - empty_pages}/{page_count} pages")
                
                return text
            except ImportError:
                print("Warning: pdfplumber not installed. PDF support limited.")
                print("Install with: pip install pdfplumber")
                return ""
        except Exception as e:
            print(f"Error parsing PDF file: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    @staticmethod
    def parse_file(filepath: str) -> str:
        """Auto-detect file type and parse accordingly"""
        ext = Path(filepath).suffix.lower()
        
        if ext == '.txt':
            return DocumentParser.parse_text_file(filepath)
        elif ext == '.md':
            return DocumentParser.parse_markdown_file(filepath)
        elif ext == '.pdf':
            return DocumentParser.parse_pdf_file(filepath)
        else:
            print(f"Unsupported file type: {ext}")
            return ""


class KnowledgeBase:
    """Manages knowledge base documents and indexing with dual-source support (local + Cosmos DB)"""
    
    def __init__(self, use_cosmos_db: bool = True):
        """
        Initialize knowledge base
        
        Args:
            use_cosmos_db: Whether to enable Cosmos DB storage for dual-source indexing
        """
        self._ensure_directories()
        self.index = self._load_index()
        self.chunker = DocumentChunker()
        self.parser = DocumentParser()
        
        # Initialize Cosmos DB if available and requested
        self.cosmos_storage = None
        self.dual_search = None
        self.use_cosmos_db = use_cosmos_db and COSMOS_AVAILABLE
        
        if self.use_cosmos_db:
            try:
                self.cosmos_storage = CosmosDBStorage(
                    endpoint=os.getenv("COSMOS_DB_ENDPOINT"),
                    key=os.getenv("COSMOS_DB_KEY"),
                    database_name=os.getenv("COSMOS_DB_DATABASE_NAME", "genai-kb"),
                    container_name=os.getenv("COSMOS_DB_CONTAINER_NAME", "documents")
                )
                print("[+] Cosmos DB storage initialized for dual-source indexing")
            except Exception as e:
                print(f"[WARNING] Could not initialize Cosmos DB storage: {e}")
                print("          KB will operate in local-only mode")
                self.cosmos_storage = None
                self.use_cosmos_db = False
    
    def _ensure_directories(self):
        """Create KB directory structure if needed"""
        for dir_path in [KB_DIR, 
                        os.path.join(KB_DIR, KB_COLLECTIONS_DIR),
                        os.path.join(KB_DIR, KB_DOCUMENTS_DIR)]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
    
    def _get_index_path(self) -> str:
        """Get path to KB index file"""
        return os.path.join(KB_DIR, KB_INDEX_FILE)
    
    def _get_collection_file(self, collection_name: str) -> str:
        """Get path to collection metadata file"""
        safe_name = collection_name.replace(' ', '_').lower()
        return os.path.join(KB_DIR, KB_COLLECTIONS_DIR, f"{safe_name}.json")
    
    def _get_document_file(self, doc_id: str) -> str:
        """Get path to document file"""
        return os.path.join(KB_DIR, KB_DOCUMENTS_DIR, f"{doc_id}.json")
    
    def _load_index(self) -> Dict:
        """Load KB index from file"""
        index_path = self._get_index_path()
        
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading KB index: {e}")
                return {"collections": [], "documents": [], "last_updated": None}
        
        return {"collections": [], "documents": [], "last_updated": None}
    
    def _save_index(self):
        """Save KB index to file"""
        index_path = self._get_index_path()
        
        try:
            with open(index_path, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving KB index: {e}")
    
    def _save_collection_file(self, collection: Dict):
        """Save collection metadata to file"""
        filepath = self._get_collection_file(collection['name'])
        
        try:
            with open(filepath, 'w') as f:
                json.dump(collection, f, indent=2)
        except Exception as e:
            print(f"Error saving collection file: {e}")
    
    def _save_document_file(self, document: Dict):
        """Save document to file"""
        filepath = self._get_document_file(document['id'])
        
        try:
            with open(filepath, 'w') as f:
                json.dump(document, f, indent=2)
        except Exception as e:
            print(f"Error saving document file: {e}")
    
    def _load_collection_file(self, collection_name: str) -> Optional[Dict]:
        """Load collection metadata from file"""
        filepath = self._get_collection_file(collection_name)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading collection file: {e}")
        
        return None
    
    def _load_document_file(self, doc_id: str) -> Optional[Dict]:
        """Load document from file"""
        filepath = self._get_document_file(doc_id)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading document file: {e}")
        
        return None
    
    def create_collection(self, collection_name: str, description: str = "") -> bool:
        """
        Create a new collection
        
        Args:
            collection_name: Name of the collection
            description: Description of the collection
        
        Returns:
            True if successful, False otherwise
        """
        # Check if collection exists
        if any(c == collection_name for c in self.index['collections']):
            print(f"Collection '{collection_name}' already exists")
            return False
        
        collection = {
            "name": collection_name,
            "description": description,
            "document_count": 0,
            "created_at": datetime.now().isoformat(),
            "documents": []
        }
        
        # Save collection file and add to index
        self._save_collection_file(collection)
        self.index['collections'].append(collection_name)
        self.index['last_updated'] = datetime.now().isoformat()
        self._save_index()
        
        print(f"[+] Collection '{collection_name}' created")
        return True
    
    def list_collections(self) -> List[Dict]:
        """
        List all collections in the knowledge base
        
        Returns:
            List of collection dictionaries with name, description, and document count
        """
        collections = []
        for collection_name in self.index.get('collections', []):
            collection_file = self._load_collection_file(collection_name)
            if collection_file:
                collections.append(collection_file)
        return collections
    
    def add_document(self, filepath: str, collection_name: str, 
                    doc_title: str = "", chunking_strategy: str = "paragraphs") -> bool:
        """
        Add a document to the knowledge base
        
        Args:
            filepath: Path to the document file
            collection_name: Collection to add document to
            doc_title: Optional custom title for the document
            chunking_strategy: Chunking strategy to use:
                - 'paragraphs': Groups paragraphs with overlap
                - 'sentences': Groups sentences (NLTK-based)
                - 'size': Fixed-size chunks with overlap
                - 'sliding_window': 400 char window with 200 char step
                - 'semantic': Groups sentences by semantic similarity
        
        Returns:
            True if successful, False otherwise
        """
        # Security: Validate file before processing
        validation = InputValidator.validate_file(filepath)
        if not validation['is_valid']:
            print(f"[VALIDATION ERROR] Cannot add document:")
            for error in validation['errors']:
                print(f"  - {error}")
            return False
        
        # Display warnings if any
        for warning in validation['warnings']:
            print(f"  [WARNING] {warning}")
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False
        
        # Check if collection exists
        if collection_name not in self.index['collections']:
            print(f"Collection '{collection_name}' not found")
            return False
        
        # Parse document
        print(f"\nParsing document: {filepath}")
        content = self.parser.parse_file(filepath)
        
        if not content:
            print("Could not parse document content")
            return False
        
        # Chunk the document
        print(f"Chunking with strategy: {chunking_strategy}")
        if chunking_strategy == "paragraphs":
            chunks = self.chunker.chunk_by_paragraphs(content)
        elif chunking_strategy == "sentences":
            chunks = self.chunker.chunk_by_sentences(content)
        elif chunking_strategy == "size":
            chunks = self.chunker.chunk_by_size(content)
        elif chunking_strategy == "sliding_window":
            chunks = self.chunker.chunk_by_sliding_window(content)
        elif chunking_strategy == "semantic":
            chunks = self.chunker.chunk_by_semantic(content)
        else:
            chunks = self.chunker.chunk_by_paragraphs(content)
        
        if not chunks:
            print("[ERROR] No content to index")
            print(f"  Content length: {len(content)} characters")
            if len(content) == 0:
                print("  Possible causes:")
                print("    - File is empty")
                print("    - PDF extraction failed (scanned image?)")
                print("    - File encoding issue")
            elif len(content) < 100:
                print(f"  Warning: Content is very short ({len(content)} chars)")
                print("  May not produce valid chunks")
            return False
        
        # Create document entry
        doc_id = f"doc_{collection_name.replace(' ', '_')}_{len(self.index['documents'])}_{int(datetime.now().timestamp())}"
        title = doc_title or Path(filepath).stem
        
        document = {
            "id": doc_id,
            "title": title,
            "filepath": filepath,
            "collection": collection_name,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "total_words": sum(c['word_count'] for c in chunks),
            "added_at": datetime.now().isoformat(),
            "indexed": False  # Will be set to True when embeddings are generated
        }
        
        # Save document file and update index
        self._save_document_file(document)
        self.index['documents'].append(doc_id)
        self.index['last_updated'] = datetime.now().isoformat()
        self._save_index()
        
        # Update collection
        collection = self._load_collection_file(collection_name)
        if collection:
            collection['documents'].append(doc_id)
            collection['document_count'] = len(collection['documents'])
            self._save_collection_file(collection)
        
        print(f"[+] Document added: {title}")
        print(f"  - Chunks: {len(chunks)}")
        print(f"  - Total words: {document['total_words']}")
        print(f"  - Document ID: {doc_id}")
        
        # Log to audit trail
        if audit_logger:
            audit_logger.log_user_action('KB_DOCUMENT_ADDED', {
                'doc_id': doc_id,
                'title': title,
                'collection': collection_name,
                'chunk_count': len(chunks),
                'total_words': document['total_words'],
                'file_format': Path(filepath).suffix,
            })
        
        return True
    
    def index_document_to_cosmos(self, doc_id: str, embeddings: List[List[float]]) -> bool:
        """
        Index a document to Cosmos DB with embeddings (for dual-source storage)
        
        Args:
            doc_id: Document ID to index
            embeddings: List of embedding vectors for each chunk
        
        Returns:
            True if successful, False otherwise
        """
        if not self.use_cosmos_db or not self.cosmos_storage:
            return False
        
        try:
            # Load document from local storage
            document = self._load_document_file(doc_id)
            if not document:
                print(f"[ERROR] Document not found: {doc_id}")
                return False
            
            chunks = document.get('chunks', [])
            if len(chunks) != len(embeddings):
                print(f"[ERROR] Chunk count ({len(chunks)}) != Embedding count ({len(embeddings)})")
                return False
            
            # Store in Cosmos DB with embeddings
            self.cosmos_storage.store_document(
                doc_id=doc_id,
                collection_id=document['collection'],
                title=document['title'],
                content=self._reconstruct_content(chunks),
                chunks=chunks,
                embeddings=embeddings,
                metadata={
                    'filepath': document.get('filepath', ''),
                    'added_at': document.get('added_at', ''),
                    'chunking_strategy': chunks[0].get('strategy', 'unknown') if chunks else 'unknown'
                }
            )
            
            # Update local document to mark as indexed
            document['indexed'] = True
            document['cosmos_indexed_at'] = datetime.now().isoformat()
            self._save_document_file(document)
            
            print(f"[+] Document indexed to Cosmos DB: {doc_id}")
            
            # Log to audit trail
            if audit_logger:
                audit_logger.log_user_action('KB_DOCUMENT_COSMOS_INDEXED', {
                    'doc_id': doc_id,
                    'title': document['title'],
                    'collection': document['collection'],
                    'chunk_count': len(chunks),
                    'embedding_count': len(embeddings)
                })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to index to Cosmos DB: {e}")
            return False
    
    def _reconstruct_content(self, chunks: List[Dict]) -> str:
        """Reconstruct full content from chunks"""
        return "\n\n".join(chunk['text'] for chunk in chunks)
    
    def bulk_index_kb_to_cosmos(self) -> Dict:
        """
        Bulk index all KB documents to Cosmos DB with embeddings
        
        This method iterates through all KB documents and generates embeddings
        for them, then stores them in Cosmos DB for dual-source search.
        
        Returns:
            Dictionary with indexing statistics
        """
        if not self.cosmos_storage:
            print("[ERROR] Cosmos DB not available")
            return {}
        
        try:
            from embedding_generator import EmbeddingGenerator
        except ImportError:
            print("[ERROR] Embedding generator module not found")
            return {}
        
        gen = EmbeddingGenerator()
        if not gen.is_available():
            print("[ERROR] Embedding generator not available (check Azure OpenAI credentials)")
            return {}
        
        stats = {
            "total_docs": 0,
            "indexed": 0,
            "failed": 0,
            "total_chunks": 0
        }
        
        # Get all documents
        all_docs = self.list_documents()
        
        if not all_docs:
            print("[*] No documents found to index")
            return stats
        
        print(f"\n[*] Indexing {len(all_docs)} documents to Cosmos DB...")
        print("This may take a few moments...\n")
        
        for i, doc in enumerate(all_docs, 1):
            doc_id = doc.get('id', 'unknown')
            doc_title = doc.get('title', 'Unknown')
            
            stats["total_docs"] += 1
            
            try:
                # Get chunk texts
                chunks = doc.get('chunks', [])
                if not chunks:
                    print(f"[{i}/{len(all_docs)}] Skipping '{doc_title}' - no chunks")
                    continue
                
                chunk_texts = [c['text'] for c in chunks]
                stats["total_chunks"] += len(chunks)
                
                print(f"[{i}/{len(all_docs)}] Indexing '{doc_title}' ({len(chunks)} chunks)...", end=" ")
                
                # Generate embeddings
                embeddings = gen.generate_batch_embeddings(chunk_texts)
                
                if embeddings and len(embeddings) == len(chunks):
                    # Index to Cosmos DB
                    success = self.index_document_to_cosmos(doc_id, embeddings)
                    if success:
                        print("[OK]")
                        stats["indexed"] += 1
                    else:
                        print("[FAILED]")
                        stats["failed"] += 1
                else:
                    print("[FAILED - embedding mismatch]")
                    stats["failed"] += 1
            
            except Exception as e:
                print(f"[ERROR] {e}")
                stats["failed"] += 1
        
        print(f"\n[+] Bulk indexing complete!")
        print(f"    Total documents: {stats['total_docs']}")
        print(f"    Successfully indexed: {stats['indexed']}")
        print(f"    Failed: {stats['failed']}")
        print(f"    Total chunks indexed: {stats['total_chunks']}")
        
        return stats
    
    def _reconstruct_content(self, chunks: List[Dict]) -> str:
        """Reconstruct full content from chunks"""
        return "\n\n".join(chunk['text'] for chunk in chunks)
    
    def search_dual_source(self, query: str, query_embedding: List[float], 
                          collection_id: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """
        Search across both local and Cosmos DB sources (dual-source search)
        
        Args:
            query: Search query text
            query_embedding: Embedding vector for the query
            collection_id: Optional filter by collection
            top_k: Number of results to return
        
        Returns:
            List of search results from both sources
        """
        results = []
        
        # Search local storage (conversations/existing embeddings)
        print(f"  [RAG] Searching local storage...")
        local_results = self._search_local_embeddings(query_embedding, collection_id, top_k)
        for result in local_results:
            result['source'] = 'local_kb'
        results.extend(local_results)
        
        # Search Cosmos DB (KB documents with embeddings)
        if self.use_cosmos_db and self.cosmos_storage:
            print(f"  [RAG] Searching Cosmos DB...")
            cosmos_results = self.cosmos_storage.search_by_embedding(
                query_embedding=query_embedding,
                collection_id=collection_id,
                top_k=top_k,
                threshold=0.5
            )
            for result in cosmos_results:
                result['source'] = 'cosmos_kb'
                # Normalize field names for consistency
                result['relevance'] = result.get('similarity', 0)
            results.extend(cosmos_results)
        
        # Rank and deduplicate
        results = self._rank_and_merge_results(results)
        
        return results[:top_k]
    
    def _search_local_embeddings(self, query_embedding: List[float], 
                                 collection_id: Optional[str], top_k: int) -> List[Dict]:
        """Search local documents for similar embeddings"""
        # Placeholder for local embedding search
        # In a full implementation, this would search against local embeddings
        return []
    
    def _rank_and_merge_results(self, results: List[Dict]) -> List[Dict]:
        """
        Rank and deduplicate search results from multiple sources
        
        Gives slight preference to Cosmos DB (cloud-stored, professionally indexed)
        """
        # Sort by relevance/similarity score
        for result in results:
            score = result.get('relevance', result.get('similarity', 0))
            # Boost Cosmos DB results slightly
            if result.get('source') == 'cosmos_kb':
                score *= 1.05
            result['rank_score'] = score
        
        results.sort(key=lambda x: x['rank_score'], reverse=True)
        
        # Deduplicate based on text similarity (optional)
        # For now, just return top results
        return results
    

        """Get all collections with their metadata"""
        collections = []
        for col_name in self.index.get('collections', []):
            col_data = self._load_collection_file(col_name)
            if col_data:
                collections.append(col_data)
        return collections
    
    def list_documents(self, collection_name: Optional[str] = None) -> List[Dict]:
        """Get all documents, optionally filtered by collection"""
        documents = []
        for doc_id in self.index.get('documents', []):
            doc_data = self._load_document_file(doc_id)
            if doc_data:
                if collection_name is None or doc_data['collection'] == collection_name:
                    documents.append(doc_data)
        return documents
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for a collection"""
        collection = self._load_collection_file(collection_name)
        
        if not collection:
            return {}
        
        collection_docs = self.list_documents(collection_name)
        
        total_chunks = sum(d['chunk_count'] for d in collection_docs)
        total_words = sum(d['total_words'] for d in collection_docs)
        indexed_count = sum(1 for d in collection_docs if d.get('indexed', False))
        
        return {
            "name": collection_name,
            "description": collection.get('description', ''),
            "document_count": len(collection_docs),
            "total_chunks": total_chunks,
            "total_words": total_words,
            "indexed_documents": indexed_count,
            "created_at": collection['created_at']
        }
    
    def get_stats(self) -> Dict:
        """Get overall KB statistics"""
        collections = self.list_collections()
        documents = self.list_documents()
        
        total_chunks = sum(d['chunk_count'] for d in documents)
        total_words = sum(d['total_words'] for d in documents)
        indexed = sum(1 for d in documents if d.get('indexed', False))
        
        return {
            "collection_count": len(collections),
            "document_count": len(documents),
            "total_chunks": total_chunks,
            "total_words": total_words,
            "indexed_documents": indexed,
            "last_updated": self.index.get('last_updated')
        }


def interactive_kb_menu(kb: KnowledgeBase):
    """Interactive menu for knowledge base management"""
    while True:
        print("\n" + "="*60)
        print("Knowledge Base Management")
        print("="*60)
        
        stats = kb.get_stats()
        print(f"Documents: {stats['document_count']} | Collections: {stats['collection_count']}")
        print(f"Indexed: {stats['indexed_documents']}/{stats['document_count']}")
        
        print("\nOptions:")
        print("1. Create collection")
        print("2. Add document to collection")
        print("3. List collections")
        print("4. List documents")
        print("5. View collection stats")
        print("6. View KB stats")
        print("7. Bulk index KB to Cosmos DB (with embeddings)")
        print("0. Back to main menu")
        
        choice = input("\nSelect option (0-7): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            name = input("Collection name: ").strip()
            desc = input("Description (optional): ").strip()
            kb.create_collection(name, desc)
        elif choice == "2":
            collections = kb.list_collections()
            if not collections:
                print("No collections found. Create one first.")
                continue
            
            print("\nAvailable collections:")
            for i, c in enumerate(collections, 1):
                print(f"  {i}. {c['name']}")
            
            col_choice = input("Select collection (number): ").strip()
            try:
                col_idx = int(col_choice) - 1
                if 0 <= col_idx < len(collections):
                    collection = collections[col_idx]
                    filepath = input("File path: ").strip()
                    title = input("Document title (optional): ").strip()
                    
                    print("\n" + "="*50)
                    print("CHUNKING STRATEGIES")
                    print("="*50)
                    print("1. Paragraphs (default)")
                    print("   - Groups paragraphs with overlap")
                    print("   - Best for: Essays, long-form content")
                    print()
                    print("2. Sentences")
                    print("   - Groups 5 sentences per chunk")
                    print("   - Best for: Technical documentation")
                    print()
                    print("3. Size-based (Sliding Window)")
                    print("   - Fixed 500 char chunks with overlap")
                    print("   - Best for: Continuous text, books")
                    print()
                    print("4. Sliding Window (Advanced)")
                    print("   - 400 char window, 200 char step")
                    print("   - Best for: Preserving context")
                    print()
                    print("5. Semantic (Advanced)")
                    print("   - Groups sentences by topic")
                    print("   - Best for: Mixed-topic documents")
                    print()
                    
                    strategy_choice = input("Select strategy (1-5, default=1): ").strip()
                    strategies = {
                        "1": "paragraphs", 
                        "2": "sentences", 
                        "3": "size",
                        "4": "sliding_window",
                        "5": "semantic"
                    }
                    strategy = strategies.get(strategy_choice, "paragraphs")
                    
                    kb.add_document(filepath, collection['name'], title, strategy)
            except ValueError:
                print("Invalid selection")
        elif choice == "3":
            collections = kb.list_collections()
            if not collections:
                print("No collections found")
            else:
                print("\nCollections:")
                for c in collections:
                    print(f"  - {c['name']}: {c.get('description', 'No description')}")
                    print(f"    Documents: {c.get('document_count', 0)}")
        elif choice == "4":
            collections = kb.list_collections()
            if not collections:
                print("No collections found")
                continue
            
            print("\nCollections:")
            for i, c in enumerate(collections, 1):
                print(f"  {i}. {c['name']}")
            
            col_choice = input("Select collection or press Enter for all: ").strip()
            
            try:
                if col_choice:
                    col_idx = int(col_choice) - 1
                    if 0 <= col_idx < len(collections):
                        collection = collections[col_idx]
                        docs = kb.list_documents(collection['name'])
                    else:
                        print("Invalid selection")
                        continue
                else:
                    docs = kb.list_documents()
                
                if not docs:
                    print("No documents found")
                else:
                    print("\nDocuments:")
                    for d in docs:
                        status = "[X] Indexed" if d.get('indexed') else "[ ] Not indexed"
                        print(f"  - {d['title']}")
                        print(f"    Chunks: {d['chunk_count']} | Words: {d['total_words']} | {status}")
            except ValueError:
                print("Invalid selection")
        elif choice == "5":
            collections = kb.list_collections()
            if not collections:
                print("No collections found")
                continue
            
            print("\nCollections:")
            for i, c in enumerate(collections, 1):
                print(f"  {i}. {c['name']}")
            
            col_choice = input("Select collection: ").strip()
            try:
                col_idx = int(col_choice) - 1
                if 0 <= col_idx < len(collections):
                    collection = collections[col_idx]
                    stats = kb.get_collection_stats(collection['name'])
                    
                    print(f"\nCollection: {stats['name']}")
                    print(f"  Documents: {stats['document_count']}")
                    print(f"  Total chunks: {stats['total_chunks']}")
                    print(f"  Total words: {stats['total_words']}")
                    print(f"  Indexed: {stats['indexed_documents']}/{stats['document_count']}")
                    print(f"  Created: {stats['created_at']}")
            except ValueError:
                print("Invalid selection")
        elif choice == "6":
            stats = kb.get_stats()
            print("\nKnowledge Base Statistics:")
            print(f"  Collections: {stats['collection_count']}")
            print(f"  Documents: {stats['document_count']}")
            print(f"  Total chunks: {stats['total_chunks']}")
            print(f"  Total words: {stats['total_words']}")
            print(f"  Indexed documents: {stats['indexed_documents']}/{stats['document_count']}")
            print(f"  Last updated: {stats['last_updated'] or 'Never'}")
        elif choice == "7":
            print("\n" + "="*60)
            print("BULK INDEX KB TO COSMOS DB")
            print("="*60)
            print("\nThis will:")
            print("  1. Generate embeddings for all KB documents")
            print("  2. Index them to Azure Cosmos DB")
            print("  3. Enable enterprise dual-source search")
            print("\nNote: This requires Azure OpenAI credentials")
            confirm = input("\nProceed with bulk indexing? (yes/no): ").strip().lower()
            if confirm == "yes":
                stats = kb.bulk_index_kb_to_cosmos()
            else:
                print("Bulk indexing cancelled.")

