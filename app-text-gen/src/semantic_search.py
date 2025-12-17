"""
Semantic Search using Azure OpenAI Embeddings
Enables searching conversations and documents using embeddings and cosine similarity
"""
import json
import os
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
try:
    from azure.ai.inference import EmbeddingsClient
    from azure.core.credentials import AzureKeyCredential
except ImportError:
    print("Warning: Azure AI Inference not available, using requests fallback")
    EmbeddingsClient = None
    AzureKeyCredential = None

EMBEDDINGS_DIR = "embeddings"
EMBEDDING_INDEX_FILE = "conversation_embeddings.json"

class AzureEmbeddings:
    """Handle Azure OpenAI Embeddings API calls"""
    
    def __init__(self):
        """Initialize Azure Embeddings client from environment"""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not self.api_key or not self.endpoint:
            raise ValueError(
                "Azure OpenAI credentials not found. "
                "Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env"
            )
        
        # Use OpenAI SDK for better compatibility with Azure OpenAI
        print("[INFO] Using OpenAI SDK configured for Azure")
        self._init_openai_client()
        self.use_openai_sdk = True
    
    def _init_openai_client(self):
        """Initialize OpenAI client configured for Azure"""
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        print("[INFO] Using OpenAI SDK configured for Azure")
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string"""
        try:
            if self.use_openai_sdk:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.deployment
                )
                return response.data[0].embedding
            else:
                response = self.client.embed(
                    input=text,
                    model=self.deployment
                )
                return response.data[0].embedding
        except Exception as e:
            print(f"Error embedding text: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts efficiently"""
        try:
            if self.use_openai_sdk:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.deployment
                )
                # OpenAI SDK returns data in order
                return [item.embedding for item in response.data]
            else:
                response = self.client.embed(
                    input=texts,
                    model=self.deployment
                )
                # Sort by index to maintain order
                embeddings_list = sorted(response.data, key=lambda x: x.index)
                return [item.embedding for item in embeddings_list]
        except Exception as e:
            print(f"Error embedding batch: {e}")
            return None

class EmbeddingIndex:
    """Manage conversation embeddings and semantic search"""
    
    def __init__(self):
        """Initialize embedding index"""
        self.embeddings_client = AzureEmbeddings()
        self.index = self._load_index()
    
    def _ensure_dir(self):
        """Create embeddings directory if it doesn't exist"""
        if not os.path.exists(EMBEDDINGS_DIR):
            os.makedirs(EMBEDDINGS_DIR)
    
    def _get_index_path(self) -> str:
        """Get path to embedding index file"""
        return os.path.join(EMBEDDINGS_DIR, EMBEDDING_INDEX_FILE)
    
    def _load_index(self) -> Dict:
        """Load existing embedding index from file"""
        index_path = self._get_index_path()
        
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}")
                return {"entries": [], "last_updated": None}
        
        return {"entries": [], "last_updated": None}
    
    def _save_index(self):
        """Save embedding index to file"""
        self._ensure_dir()
        index_path = self._get_index_path()
        
        try:
            with open(index_path, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def index_conversation(self, conversation_id: str, messages: List[Dict], 
                          system_prompt: str, model: str):
        """
        Index a conversation by creating message pair embeddings
        
        Args:
            conversation_id: Unique conversation identifier
            messages: List of message dicts with "role" and "content"
            system_prompt: The system prompt used
            model: Model used in conversation
        """
        print(f"\nIndexing conversation: {conversation_id}")
        
        # Extract message pairs (user + assistant)
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        pairs_to_embed = []
        pair_metadata = []
        
        # Create pairs
        for i, user_msg in enumerate(user_messages):
            if i < len(assistant_messages):
                assistant_msg = assistant_messages[i]
                
                # Combine user and assistant message for richer context
                combined_text = f"User: {user_msg.get('content', '')}\n\nAssistant: {assistant_msg.get('content', '')}"
                pairs_to_embed.append(combined_text)
                
                pair_metadata.append({
                    "pair_id": f"{conversation_id}_pair_{i}",
                    "conversation_id": conversation_id,
                    "user_message": user_msg.get('content', ''),
                    "assistant_message": assistant_msg.get('content', ''),
                    "pair_index": i,
                    "model": model,
                    "system_prompt": system_prompt,
                    "timestamp": datetime.now().isoformat()
                })
        
        if not pairs_to_embed:
            print(f"  No message pairs found to index")
            return
        
        # Get embeddings
        print(f"  Generating embeddings for {len(pairs_to_embed)} message pairs...")
        embeddings = self.embeddings_client.embed_batch(pairs_to_embed)
        
        if embeddings is None:
            print(f"  Error generating embeddings")
            return
        
        # Add to index
        for metadata, embedding in zip(pair_metadata, embeddings):
            entry = {
                **metadata,
                "embedding": embedding,
                "similarity_score": None
            }
            
            # Check if entry already exists and update
            existing = [e for e in self.index["entries"] if e.get("pair_id") == metadata["pair_id"]]
            if existing:
                idx = self.index["entries"].index(existing[0])
                self.index["entries"][idx] = entry
            else:
                self.index["entries"].append(entry)
        
        self.index["last_updated"] = datetime.now().isoformat()
        self._save_index()
        
        print(f"  ✓ Indexed {len(pairs_to_embed)} message pairs")
    
    def search(self, query: str, top_k: int = 5, similarity_threshold: float = 0.5) -> List[Dict]:
        """
        Search the embedding index using semantic similarity
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score (0.0-1.0)
        
        Returns:
            List of matching entries sorted by similarity
        """
        if not self.index["entries"]:
            return []
        
        # Embed the query
        print(f"\nSearching embeddings for: '{query}'")
        query_embedding = self.embeddings_client.embed_text(query)
        
        if query_embedding is None:
            print("Error embedding query")
            return []
        
        # Convert to numpy array
        query_vector = np.array([query_embedding])
        
        # Calculate similarity scores
        results = []
        
        for entry in self.index["entries"]:
            embedding = np.array([entry["embedding"]])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(query_vector, embedding)[0][0]
            
            if similarity >= similarity_threshold:
                result = entry.copy()
                result["similarity_score"] = float(similarity)
                results.append(result)
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results[:top_k]
    
    def search_by_conversation(self, query: str, conversation_id: str, 
                              top_k: int = 3) -> List[Dict]:
        """Search within a specific conversation"""
        all_results = self.search(query, top_k=100)
        
        # Filter by conversation_id
        conversation_results = [
            r for r in all_results 
            if r.get("conversation_id") == conversation_id
        ]
        
        return conversation_results[:top_k]
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the embedding index"""
        entries = self.index.get("entries", [])
        
        # Count by conversation
        conversations = set(e.get("conversation_id") for e in entries)
        
        # Count by model
        models = {}
        for entry in entries:
            model = entry.get("model", "unknown")
            models[model] = models.get(model, 0) + 1
        
        return {
            "total_entries": len(entries),
            "total_conversations": len(conversations),
            "by_model": models,
            "last_updated": self.index.get("last_updated"),
            "index_file_size": os.path.getsize(self._get_index_path()) if os.path.exists(self._get_index_path()) else 0
        }
    
    def display_index_stats(self):
        """Display embedding index statistics"""
        stats = self.get_index_stats()
        
        print("\n" + "=" * 60)
        print("Embedding Index Statistics")
        print("=" * 60)
        
        print(f"\nTotal Indexed Entries:    {stats['total_entries']}")
        print(f"Total Conversations:      {stats['total_conversations']}")
        print(f"Last Updated:             {stats['last_updated']}")
        print(f"Index Size:               {stats['index_file_size']:,} bytes")
        
        if stats['by_model']:
            print(f"\nEntries by Model:")
            for model, count in sorted(stats['by_model'].items()):
                print(f"  {model}: {count}")
        
        print("=" * 60)

def display_search_results(results: List[Dict]):
    """Display search results in formatted way"""
    if not results:
        print("\nNo results found.")
        return
    
    print("\n" + "=" * 60)
    print(f"Semantic Search Results ({len(results)} matches)")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        similarity = result.get("similarity_score", 0)
        model = result.get("model", "Unknown")
        timestamp = result.get("timestamp", "Unknown")
        
        # Color similarity score
        if similarity >= 0.9:
            quality = "Excellent"
        elif similarity >= 0.8:
            quality = "Very Good"
        elif similarity >= 0.7:
            quality = "Good"
        else:
            quality = "Fair"
        
        print(f"\n{i}. Similarity: {similarity:.2%} ({quality})")
        print(f"   Model: {model} | Time: {timestamp}")
        
        user_msg = result.get("user_message", "")
        assistant_msg = result.get("assistant_message", "")
        
        print(f"   User:      {user_msg[:80]}..." if len(user_msg) > 80 else f"   User:      {user_msg}")
        print(f"   Assistant: {assistant_msg[:80]}..." if len(assistant_msg) > 80 else f"   Assistant: {assistant_msg}")
    
    print("\n" + "=" * 60)

def interactive_semantic_search(embedding_index: EmbeddingIndex):
    """Interactive semantic search interface"""
    similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.75"))
    
    print("\n" + "=" * 60)
    print("Semantic Search")
    print("=" * 60)
    
    query = input("\nEnter search query: ").strip()
    
    if not query:
        print("Query cannot be empty.")
        return
    
    results = embedding_index.search(query, top_k=5, similarity_threshold=similarity_threshold)
    display_search_results(results)
    
    return results

