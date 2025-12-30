"""
Azure Cosmos DB Storage for Knowledge Base Vector Database

This module provides integration with Azure Cosmos DB for storing
KB documents with embeddings and advanced search capabilities.
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

class CosmosDBStorage:
    """
    Handles storage and retrieval of KB documents in Azure Cosmos DB
    
    Features:
    - Vector embedding storage
    - Semantic search capabilities
    - Metadata indexing
    - Dual-source compatibility with local JSONL storage
    """
    
    def __init__(self, 
                 endpoint: str,
                 key: str,
                 database_name: str,
                 container_name: str):
        """
        Initialize Cosmos DB storage
        
        Args:
            endpoint: Cosmos DB endpoint URL
            key: Cosmos DB primary key
            database_name: Database name
            container_name: Container name for documents
        """
        self.endpoint = endpoint
        self.key = key
        self.database_name = database_name
        self.container_name = container_name
        self.client = None
        self.database = None
        self.container = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure Cosmos DB client"""
        try:
            from azure.cosmos import CosmosClient, PartitionKey
            
            self.client = CosmosClient(self.endpoint, self.key)
            
            # Get or create database
            self.database = self.client.get_database_client(self.database_name)
            
            # Get or create container with vector search enabled
            self.container = self.database.get_container_client(self.container_name)
            
            print(f"[OK] Connected to Cosmos DB")
            print(f"    Database: {self.database_name}")
            print(f"    Container: {self.container_name}")
            
        except ImportError:
            raise RuntimeError(
                "azure-cosmos not installed. Install with: pip install azure-cosmos"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Cosmos DB client: {e}")
    
    def store_document(self,
                      doc_id: str,
                      collection_id: str,
                      title: str,
                      content: str,
                      chunks: List[Dict],
                      embeddings: List[List[float]],
                      metadata: Dict = None) -> bool:
        """
        Store a KB document with embeddings in Cosmos DB
        
        Args:
            doc_id: Unique document ID
            collection_id: Collection this document belongs to
            title: Document title
            content: Full document content
            chunks: List of document chunks
            embeddings: Embeddings for each chunk
            metadata: Additional metadata
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if len(chunks) != len(embeddings):
                print(f"[ERROR] Chunk count ({len(chunks)}) != Embedding count ({len(embeddings)})")
                return False
            
            document = {
                "id": doc_id,
                "collection_id": collection_id,
                "title": title,
                "content": content,
                "created_at": datetime.now().isoformat(),
                "indexed_at": datetime.now().isoformat(),
                "chunks": [],
                "metadata": metadata or {}
            }
            
            # Add chunks with embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                document["chunks"].append({
                    "chunk_id": f"{doc_id}_chunk_{i}",
                    "text": chunk.get("text", ""),
                    "word_count": chunk.get("word_count", 0),
                    "embedding": embedding,
                    "index": i,
                    "strategy": chunk.get("strategy", "unknown")
                })
            
            # Store in Cosmos DB
            self.container.upsert_item(document)
            
            print(f"[OK] Stored document in Cosmos DB")
            print(f"    ID: {doc_id}")
            print(f"    Chunks: {len(chunks)}")
            print(f"    With embeddings: {len(embeddings)}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to store document: {e}")
            return False
    
    def search_by_embedding(self,
                           query_embedding: List[float],
                           collection_id: Optional[str] = None,
                           top_k: int = 5,
                           threshold: float = 0.5) -> List[Dict]:
        """
        Search for similar documents using embedding similarity
        
        Args:
            query_embedding: Query embedding vector
            collection_id: Filter by collection (optional)
            top_k: Number of results to return
            threshold: Minimum similarity threshold (0-1)
        
        Returns:
            List of similar chunks with scores
        """
        try:
            # Cosmos DB vector search query - simplified
            if collection_id:
                query = """
                SELECT 
                    c.id,
                    c.title,
                    c.collection_id,
                    ch.chunk_id,
                    ch.text,
                    ch.word_count,
                    ch.strategy,
                    ch.embedding
                FROM c
                JOIN ch IN c.chunks
                WHERE c.collection_id = @collection_id
                """
                parameters = [{"name": "@collection_id", "value": collection_id}]
            else:
                query = """
                SELECT 
                    c.id,
                    c.title,
                    c.collection_id,
                    ch.chunk_id,
                    ch.text,
                    ch.word_count,
                    ch.strategy,
                    ch.embedding
                FROM c
                JOIN ch IN c.chunks
                """
                parameters = []
            
            # Execute query
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            # Calculate similarity scores
            results = []
            for item in items:
                embedding = item.get("embedding", [])
                if embedding:  # Only process if embedding exists
                    similarity = self._cosine_similarity(
                        query_embedding,
                        embedding
                    )
                    
                    if similarity >= threshold:
                        results.append({
                            "doc_id": item["id"],
                            "title": item["title"],
                            "collection_id": item["collection_id"],
                            "chunk_id": item["chunk_id"],
                            "text": item["text"],
                            "similarity": similarity,
                            "strategy": item.get("strategy", "unknown")
                        })
            
            # Sort by similarity and return top k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []
    
    def search_by_keyword(self,
                         keyword: str,
                         collection_id: Optional[str] = None,
                         top_k: int = 5) -> List[Dict]:
        """
        Search for documents using keyword matching
        
        Args:
            keyword: Search keyword
            collection_id: Filter by collection (optional)
            top_k: Number of results to return
        
        Returns:
            List of matching chunks
        """
        try:
            query = """
            SELECT 
                c.id,
                c.title,
                c.collection_id,
                ch.chunk_id,
                ch.text,
                ch.word_count
            FROM c
            JOIN ch IN c.chunks
            WHERE CONTAINS(UPPER(ch.text), UPPER(@keyword))
            """
            
            if collection_id:
                query += f" AND c.collection_id = '{collection_id}'"
            
            parameters = [
                {"name": "@keyword", "value": keyword}
            ]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
                max_item_count=top_k
            ))
            
            results = []
            for item in items:
                results.append({
                    "doc_id": item["id"],
                    "title": item["title"],
                    "collection_id": item["collection_id"],
                    "chunk_id": item["chunk_id"],
                    "text": item["text"]
                })
            
            return results[:top_k]
            
        except Exception as e:
            print(f"[ERROR] Keyword search failed: {e}")
            return []
    
    def get_document(self, doc_id: str, collection_id: str) -> Optional[Dict]:
        """
        Retrieve a document by ID
        
        Args:
            doc_id: Document ID
            collection_id: Collection ID (partition key)
        
        Returns:
            Document data or None if not found
        """
        try:
            item = self.container.read_item(item=doc_id, partition_key=collection_id)
            return item
        except Exception as e:
            print(f"[ERROR] Failed to retrieve document: {e}")
            return None
    
    def list_documents(self, collection_id: str) -> List[Dict]:
        """
        List all documents in a collection
        
        Args:
            collection_id: Collection ID
        
        Returns:
            List of document summaries
        """
        try:
            query = """
            SELECT c.id, c.title, c.created_at, ARRAY_LENGTH(c.chunks) as chunk_count
            FROM c
            WHERE c.collection_id = @collection_id
            ORDER BY c.created_at DESC
            """
            
            parameters = [
                {"name": "@collection_id", "value": collection_id}
            ]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return items
            
        except Exception as e:
            print(f"[ERROR] Failed to list documents: {e}")
            return []
    
    def delete_document(self, doc_id: str, collection_id: str) -> bool:
        """
        Delete a document from Cosmos DB
        
        Args:
            doc_id: Document ID
            collection_id: Collection ID (partition key)
        
        Returns:
            True if successful
        """
        try:
            self.container.delete_item(item=doc_id, partition_key=collection_id)
            print(f"[OK] Deleted document: {doc_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete document: {e}")
            return False
    
    def get_collection_stats(self, collection_id: str) -> Dict:
        """
        Get statistics for a collection
        
        Args:
            collection_id: Collection ID
        
        Returns:
            Collection statistics
        """
        try:
            query = """
            SELECT 
                VALUE COUNT(1) as doc_count,
                SUM(ARRAY_LENGTH(c.chunks)) as total_chunks
            FROM c
            WHERE c.collection_id = @collection_id
            """
            
            parameters = [
                {"name": "@collection_id", "value": collection_id}
            ]
            
            results = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if results:
                stat = results[0]
                return {
                    "collection_id": collection_id,
                    "document_count": stat.get("doc_count", 0),
                    "total_chunks": stat.get("total_chunks", 0),
                    "indexed": True
                }
            
            return {
                "collection_id": collection_id,
                "document_count": 0,
                "total_chunks": 0,
                "indexed": False
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get collection stats: {e}")
            return {}
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Cosine similarity score (0-1)
        """
        if not vec1 or not vec2:
            return 0.0
        
        if len(vec1) != len(vec2):
            return 0.0
        
        try:
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Calculate magnitudes
            mag1 = sum(a * a for a in vec1) ** 0.5
            mag2 = sum(b * b for b in vec2) ** 0.5
            
            if mag1 == 0 or mag2 == 0:
                return 0.0
            
            return dot_product / (mag1 * mag2)
        except:
            return 0.0


class DualSourceSearch:
    """
    Implements hybrid search across local JSONL and Cosmos DB sources
    
    Combines results from:
    - Local JSONL: Conversation history
    - Cosmos DB: KB documents with vector search
    """
    
    def __init__(self, local_storage, cosmos_storage):
        """
        Initialize dual-source search
        
        Args:
            local_storage: Local JSONL storage instance
            cosmos_storage: Cosmos DB storage instance
        """
        self.local = local_storage
        self.cosmos = cosmos_storage
    
    def search(self,
               query: str,
               embedding: List[float],
               search_local: bool = True,
               search_cosmos: bool = True,
               top_k: int = 5) -> List[Dict]:
        """
        Search across both local and Cosmos DB sources
        
        Args:
            query: Search query
            embedding: Query embedding
            search_local: Search local storage
            search_cosmos: Search Cosmos DB
            top_k: Results per source
        
        Returns:
            Merged and ranked results
        """
        results = []
        
        # Search local storage
        if search_local and self.local:
            local_results = self.local.search_embeddings(embedding, top_k=top_k)
            for result in local_results:
                result["source"] = "local"
            results.extend(local_results)
        
        # Search Cosmos DB
        if search_cosmos and self.cosmos:
            cosmos_results = self.cosmos.search_by_embedding(embedding, top_k=top_k)
            for result in cosmos_results:
                result["source"] = "cosmos"
            results.extend(cosmos_results)
        
        # Rank and merge results
        results = self._rank_results(results)
        
        return results[:top_k]
    
    @staticmethod
    def _rank_results(results: List[Dict]) -> List[Dict]:
        """
        Rank and deduplicate search results
        
        Args:
            results: Mixed results from multiple sources
        
        Returns:
            Ranked results
        """
        # Simple ranking: score-based with source weight
        for result in results:
            if result["source"] == "cosmos":
                result["rank_score"] = result.get("similarity", 0) * 1.1
            else:
                result["rank_score"] = result.get("relevance", 0)
        
        # Sort by rank score
        results.sort(key=lambda x: x["rank_score"], reverse=True)
        
        return results

