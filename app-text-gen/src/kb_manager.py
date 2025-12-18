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


KB_DIR = "knowledge_base"
KB_INDEX_FILE = "kb_index.json"
KB_COLLECTIONS_DIR = "collections"
KB_DOCUMENTS_DIR = "documents"


class DocumentChunker:
    """Handles document chunking strategies"""
    
    @staticmethod
    def chunk_by_paragraphs(text: str, overlap: int = 100) -> List[Dict]:
        """
        Chunk text by paragraphs with overlap
        
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
                    "word_count": len(current_chunk.split())
                })
                # Add overlap
                current_chunk = current_chunk[-overlap:] + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "word_count": len(current_chunk.split())
            })
        
        return chunks
    
    @staticmethod
    def chunk_by_sentences(text: str, sentence_count: int = 5, overlap: int = 1) -> List[Dict]:
        """
        Chunk text by sentence groups
        
        Args:
            text: The text to chunk
            sentence_count: Number of sentences per chunk
            overlap: Number of sentences to overlap
        
        Returns:
            List of chunk dicts with text and metadata
        """
        # Simple sentence splitting (handles ., !, ?)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), sentence_count - overlap):
            chunk_sentences = sentences[i:i + sentence_count]
            if chunk_sentences:
                chunk_text = " ".join(chunk_sentences)
                chunks.append({
                    "text": chunk_text,
                    "word_count": len(chunk_text.split())
                })
        
        return chunks
    
    @staticmethod
    def chunk_by_size(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """
        Chunk text by character size with overlap
        
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
                    "word_count": len(chunk_text.split())
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
        """Parse a PDF file (basic support without external libraries)"""
        try:
            # Try using pdfplumber if available, otherwise return placeholder
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(filepath) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                print("Warning: pdfplumber not installed. PDF support limited.")
                print("Install with: pip install pdfplumber")
                return ""
        except Exception as e:
            print(f"Error parsing PDF file: {e}")
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
    """Manages knowledge base documents and indexing"""
    
    def __init__(self):
        """Initialize knowledge base"""
        self._ensure_directories()
        self.index = self._load_index()
        self.chunker = DocumentChunker()
        self.parser = DocumentParser()
    
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
    
    def add_document(self, filepath: str, collection_name: str, 
                    doc_title: str = "", chunking_strategy: str = "paragraphs") -> bool:
        """
        Add a document to the knowledge base
        
        Args:
            filepath: Path to the document file
            collection_name: Collection to add document to
            doc_title: Optional custom title for the document
            chunking_strategy: 'paragraphs', 'sentences', or 'size'
        
        Returns:
            True if successful, False otherwise
        """
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
        else:
            chunks = self.chunker.chunk_by_paragraphs(content)
        
        if not chunks:
            print("No content to index")
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
        
        return True
    
    def list_collections(self) -> List[Dict]:
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
        print("0. Back to main menu")
        
        choice = input("\nSelect option (0-6): ").strip()
        
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
                    
                    print("\nChunking strategies:")
                    print("1. Paragraphs (default)")
                    print("2. Sentences")
                    print("3. Size-based")
                    
                    strategy_choice = input("Select strategy (1-3): ").strip()
                    strategies = {"1": "paragraphs", "2": "sentences", "3": "size"}
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
