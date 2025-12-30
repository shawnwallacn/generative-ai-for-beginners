"""
Embedding Generator for Phase 2c: Dual-Source RAG with Vector Search

Generates embeddings for KB documents and queries using Azure OpenAI,
enabling semantic similarity search in Cosmos DB.
"""

import os
from typing import List, Optional
from datetime import datetime

class EmbeddingGenerator:
    """Generate embeddings using Azure OpenAI API"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 deployment_name: Optional[str] = None,
                 api_version: str = "2024-02-01",
                 embedding_dimension: int = 1536):
        """
        Initialize embedding generator with Azure OpenAI
        
        Args:
            api_key: Azure OpenAI API key (from env if not provided)
            endpoint: Azure OpenAI endpoint (from env if not provided)
            deployment_name: Embedding model deployment name
            api_version: API version to use
            embedding_dimension: Expected embedding dimension (1536 for text-embedding-3-small)
        """
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "text-embedding-3-small")
        self.api_version = api_version
        self.embedding_dimension = embedding_dimension
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure OpenAI client"""
        try:
            from openai import AzureOpenAI
            
            if not self.api_key or not self.endpoint:
                print("[WARNING] Embedding Generator: Missing Azure OpenAI credentials")
                print("          Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")
                return
            
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            print(f"[OK] Embedding Generator initialized")
            print(f"    Model: {self.deployment_name}")
            print(f"    Dimension: {self.embedding_dimension}")
            
        except ImportError:
            print("[WARNING] openai not installed")
            print("          Install with: pip install openai")
            self.client = None
        except Exception as e:
            print(f"[WARNING] Failed to initialize Embedding Generator: {e}")
            self.client = None
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None if failed
        """
        if not self.client:
            print("[ERROR] Embedding generator not initialized")
            return None
        
        try:
            if not text or not text.strip():
                print("[WARNING] Empty text provided for embedding")
                return None
            
            response = self.client.embeddings.create(
                input=text,
                model=self.deployment_name
            )
            
            if response.data:
                embedding = response.data[0].embedding
                
                # Validate embedding dimension
                if len(embedding) != self.embedding_dimension:
                    print(f"[WARNING] Unexpected embedding dimension: {len(embedding)} (expected {self.embedding_dimension})")
                
                return embedding
            else:
                print("[ERROR] No embedding data in response")
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to generate embedding: {e}")
            return None
    
    def generate_batch_embeddings(self, texts: List[str], 
                                 show_progress: bool = True) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress indicator
        
        Returns:
            List of embedding vectors (None for failed items)
        """
        if not self.client:
            print("[ERROR] Embedding generator not initialized")
            return [None] * len(texts)
        
        try:
            if not texts:
                print("[WARNING] Empty text list provided")
                return []
            
            # Filter out empty texts
            valid_texts = [t for t in texts if t and t.strip()]
            if len(valid_texts) < len(texts):
                print(f"[WARNING] Filtered out {len(texts) - len(valid_texts)} empty texts")
            
            if show_progress:
                print(f"[*] Generating embeddings for {len(valid_texts)} text(s)...")
            
            # Generate embeddings
            response = self.client.embeddings.create(
                input=valid_texts,
                model=self.deployment_name
            )
            
            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)
            
            if show_progress:
                print(f"[OK] Generated {len(embeddings)} embedding(s)")
            
            return embeddings
            
        except Exception as e:
            print(f"[ERROR] Batch embedding generation failed: {e}")
            return [None] * len(texts)
    
    def generate_chunk_embeddings(self, chunks: List[dict]) -> List[List[float]]:
        """
        Generate embeddings for KB document chunks
        
        Args:
            chunks: List of chunk dicts with 'text' field
        
        Returns:
            List of embedding vectors
        """
        if not chunks:
            return []
        
        # Extract text from chunks
        texts = [chunk.get('text', '') for chunk in chunks]
        
        print(f"[*] Generating embeddings for {len(chunks)} chunk(s)...")
        embeddings = self.generate_batch_embeddings(texts, show_progress=False)
        print(f"[OK] Generated {len(embeddings)} chunk embedding(s)")
        
        return embeddings
    
    def is_available(self) -> bool:
        """Check if embedding generator is properly initialized"""
        return self.client is not None
    
    def get_config(self) -> dict:
        """Get current configuration"""
        return {
            "endpoint": self.endpoint,
            "deployment": self.deployment_name,
            "api_version": self.api_version,
            "dimension": self.embedding_dimension,
            "available": self.is_available()
        }


class EmbeddingCache:
    """Simple in-memory cache for embeddings (can be extended with file-based caching)"""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize embedding cache
        
        Args:
            max_size: Maximum number of embeddings to cache
        """
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        if text in self.cache:
            self.hits += 1
            return self.cache[text]
        self.misses += 1
        return None
    
    def set(self, text: str, embedding: List[float]) -> bool:
        """Store embedding in cache"""
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[text] = embedding
        return True
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%"
        }


# Global embedding generator instance
_embedding_generator = None
_embedding_cache = None

def get_embedding_generator() -> Optional[EmbeddingGenerator]:
    """Get or create global embedding generator instance"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator

def get_embedding_cache() -> EmbeddingCache:
    """Get or create global embedding cache"""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache()
    return _embedding_cache

def generate_embedding(text: str, use_cache: bool = True) -> Optional[List[float]]:
    """
    Generate embedding for text with optional caching
    
    Args:
        text: Text to embed
        use_cache: Whether to use caching
    
    Returns:
        Embedding vector
    """
    generator = get_embedding_generator()
    if not generator or not generator.is_available():
        return None
    
    # Check cache
    if use_cache:
        cache = get_embedding_cache()
        cached = cache.get(text)
        if cached is not None:
            return cached
    
    # Generate embedding
    embedding = generator.generate_embedding(text)
    
    # Store in cache
    if embedding and use_cache:
        cache = get_embedding_cache()
        cache.set(text, embedding)
    
    return embedding

def generate_batch_embeddings(texts: List[str], use_cache: bool = True) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts with optional caching
    
    Args:
        texts: List of texts
        use_cache: Whether to use caching
    
    Returns:
        List of embedding vectors
    """
    generator = get_embedding_generator()
    if not generator or not generator.is_available():
        return [None] * len(texts)
    
    # Check cache for each text
    embeddings = []
    uncached_texts = []
    uncached_indices = []
    
    if use_cache:
        cache = get_embedding_cache()
        for i, text in enumerate(texts):
            cached = cache.get(text)
            if cached is not None:
                embeddings.append((i, cached))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
    else:
        uncached_texts = texts
        uncached_indices = list(range(len(texts)))
    
    # Generate uncached embeddings
    if uncached_texts:
        new_embeddings = generator.generate_batch_embeddings(uncached_texts, show_progress=False)
        
        # Store in cache
        if use_cache:
            cache = get_embedding_cache()
            for text, embedding in zip(uncached_texts, new_embeddings):
                if embedding:
                    cache.set(text, embedding)
        
        # Add to results
        for idx, embedding in zip(uncached_indices, new_embeddings):
            embeddings.append((idx, embedding))
    
    # Sort back to original order and extract embeddings
    embeddings.sort(key=lambda x: x[0])
    return [e[1] for e in embeddings]

