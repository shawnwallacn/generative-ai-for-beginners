"""
RAG (Retrieval-Augmented Generation) module for augmenting prompts with relevant context
from indexed conversations using semantic search.
"""

import os
import json
from typing import Dict, List, Tuple, Optional
from semantic_search import EmbeddingIndex


class RAGEngine:
    """Manages RAG functionality for context-aware responses"""
    
    def __init__(self, embedding_index: Optional[EmbeddingIndex] = None):
        """Initialize RAG engine with embedding index"""
        self.embedding_index = embedding_index
        self.enabled = False
        self.similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.15"))
        self.max_context_tokens = int(os.getenv("RAG_MAX_CONTEXT_TOKENS", "2000"))
        self.context_count = int(os.getenv("RAG_CONTEXT_COUNT", "3"))
        
    def enable(self):
        """Enable RAG augmentation"""
        if not self.embedding_index:
            print("⚠️ RAG cannot be enabled: Embedding index not available")
            return False
        self.enabled = True
        print("✓ RAG enabled")
        return True
    
    def disable(self):
        """Disable RAG augmentation"""
        self.enabled = False
        print("✓ RAG disabled")
    
    def toggle(self):
        """Toggle RAG on/off"""
        if self.enabled:
            self.disable()
        else:
            self.enable()
    
    def get_status(self) -> str:
        """Get RAG status"""
        status = "🟢 ON" if self.enabled else "🔴 OFF"
        return f"RAG: {status} | Threshold: {self.similarity_threshold:.2f} | Context: {self.context_count} snippets"
    
    def retrieve_context(self, query: str) -> Tuple[List[Dict], float]:
        """
        Retrieve relevant context for a query using semantic search.
        Searches both conversations and KB documents.
        
        Returns:
            Tuple of (context_results, average_similarity)
        """
        if not self.enabled or not self.embedding_index:
            return [], 0.0
        
        try:
            # Search all sources (conversations + KB)
            results = self.embedding_index.search(
                query,
                similarity_threshold=self.similarity_threshold,
                top_k=self.context_count
            )
            
            if not results:
                return [], 0.0
            
            # Calculate average similarity
            avg_similarity = sum(r['similarity_score'] for r in results) / len(results)
            return results, avg_similarity
            
        except Exception as e:
            print(f"[DEBUG] Error retrieving context: {e}")
            return [], 0.0
    
    def format_context(self, context_results: List[Dict]) -> str:
        """Format retrieved context for inclusion in prompt"""
        if not context_results:
            return ""
        
        formatted_context = "\n\n=== RELEVANT CONTEXT FROM YOUR KNOWLEDGE BASE ===\n"
        
        for i, result in enumerate(context_results, 1):
            similarity_pct = result['similarity_score'] * 100
            
            # Check if this is a KB document or conversation
            if result.get('type') == 'kb_document':
                # KB document chunk
                doc_title = result.get('doc_title', 'Unknown')
                formatted_context += f"\n[KB Context {i} - Relevance: {similarity_pct:.1f}%]\n"
                formatted_context += f"Document: {doc_title}\n"
                formatted_context += f"Collection: {result.get('collection', 'Unknown')}\n"
                formatted_context += f"Text: {result.get('text', '')[:300]}...\n"
            else:
                # Conversation pair
                formatted_context += f"\n[Conversation {i} - Relevance: {similarity_pct:.1f}%]\n"
                formatted_context += f"User: {result.get('user_message', '')[:200]}...\n"
                formatted_context += f"Assistant: {result.get('assistant_message', '')[:200]}...\n"
        
        formatted_context += "\n=== END CONTEXT ===\n"
        return formatted_context
    
    def augment_prompt(
        self, 
        original_prompt: str,
        system_prompt: str,
        context_results: Optional[List[Dict]] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Augment the original prompt with context.
        
        Returns:
            Tuple of (augmented_prompt, context_results)
        """
        if not self.enabled:
            return original_prompt, []
        
        if context_results is None:
            context_results, _ = self.retrieve_context(original_prompt)
        
        if not context_results:
            return original_prompt, []
        
        # Format context for inclusion
        formatted_context = self.format_context(context_results)
        
        # Create augmented system prompt with context
        augmented_system = (
            f"{system_prompt}\n\n"
            f"Use the following context from previous conversations to provide more accurate and informed responses:\n"
            f"{formatted_context}"
        )
        
        return original_prompt, context_results
    
    def get_augmented_system_prompt(
        self,
        original_system: str,
        context_results: List[Dict]
    ) -> str:
        """Get system prompt augmented with context"""
        if not context_results:
            return original_system
        
        formatted_context = self.format_context(context_results)
        return (
            f"{original_system}\n\n"
            f"Use the following context from previous conversations to provide more accurate and informed responses:\n"
            f"{formatted_context}"
        )
    
    def display_context_info(self, context_results: List[Dict], query: str):
        """Display information about retrieved context"""
        if not context_results:
            print("\n[RAG] No relevant context found for this query")
            return
        
        print(f"\n[RAG] Found {len(context_results)} relevant context(s):")
        for i, result in enumerate(context_results, 1):
            similarity_pct = result['similarity_score'] * 100
            source_type = "KB Document" if result.get('type') == 'kb_document' else "Conversation"
            source_info = result.get('doc_title') if result.get('type') == 'kb_document' else result.get('model', 'unknown')
            print(f"  {i}. [{source_type}] Relevance: {similarity_pct:.1f}% | {source_info}")


def interactive_rag_settings(rag_engine: RAGEngine):
    """Interactive menu for RAG settings"""
    while True:
        print("\n" + "="*60)
        print("RAG Settings")
        print("="*60)
        print(f"Status: {rag_engine.get_status()}")
        print(f"Max Context Tokens: {rag_engine.max_context_tokens}")
        print("Options:")
        print("1. Toggle RAG on/off")
        print("2. Set similarity threshold")
        print("3. Set context count (snippets)")
        print("4. Set max context tokens")
        print("0. Back to main menu")
        
        choice = input("\nSelect option (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            rag_engine.toggle()
        elif choice == "2":
            try:
                threshold = float(input("Enter similarity threshold (0.0-1.0): "))
                if 0.0 <= threshold <= 1.0:
                    rag_engine.similarity_threshold = threshold
                    print(f"✓ Threshold set to {threshold:.2f}")
                else:
                    print("Invalid range")
            except ValueError:
                print("Invalid input")
        elif choice == "3":
            try:
                count = int(input("Enter number of context snippets (1-10): "))
                if 1 <= count <= 10:
                    rag_engine.context_count = count
                    print(f"✓ Context count set to {count}")
                else:
                    print("Invalid range")
            except ValueError:
                print("Invalid input")
        elif choice == "4":
            try:
                tokens = int(input("Enter max context tokens (500-5000): "))
                if 500 <= tokens <= 5000:
                    rag_engine.max_context_tokens = tokens
                    print(f"✓ Max context tokens set to {tokens}")
                else:
                    print("Invalid range")
            except ValueError:
                print("Invalid input")
        else:
            print("Invalid choice")

