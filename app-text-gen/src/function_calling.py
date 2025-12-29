"""
Function Calling Module for AI-Powered Tool Integration

This module enables the LLM to intelligently call tools based on user requests.
It defines function schemas that the LLM can use and implements the actual
Python functions that perform the work.

Key Concepts:
- Function Schemas: JSON definitions that tell the LLM what functions exist
- Function Calls: When the LLM decides to call a function with specific arguments
- Function Execution: We execute the Python function and send results back to LLM
"""

import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime


class FunctionDefinitions:
    """
    Defines all available functions that the LLM can call.
    Each function has a name, description, and parameter schema.
    """
    
    @staticmethod
    def get_all_functions() -> List[Dict[str, Any]]:
        """
        Returns all available function definitions for the LLM.
        
        These are passed to the OpenAI API in the 'functions' parameter.
        The LLM uses these to understand what it can do.
        """
        return [
            FunctionDefinitions.search_knowledge_base(),
            FunctionDefinitions.get_kb_document(),
            FunctionDefinitions.get_kb_stats(),
            FunctionDefinitions.extract_code_snippet(),
            FunctionDefinitions.create_summary(),
        ]
    
    # ==================== Phase 1: KB Query Functions ====================
    
    @staticmethod
    def search_knowledge_base() -> Dict[str, Any]:
        """
        Function definition for searching the Knowledge Base.
        
        The LLM will call this when the user asks questions about
        stored documents (e.g., "What's in the 6502 docs?")
        """
        return {
            "name": "search_knowledge_base",
            "description": "Search the Knowledge Base for relevant documents based on a query. Use this when the user asks about topics covered in stored documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant KB documents"
                    },
                    "collection": {
                        "type": "string",
                        "description": "Optional: Specific collection to search in (e.g., '6502-docs'). Leave empty to search all."
                    }
                },
                "required": ["query"]
            }
        }
    
    @staticmethod
    def get_kb_document() -> Dict[str, Any]:
        """
        Function definition for retrieving a specific KB document.
        
        Use this to get the full content of a specific document
        when the user needs detailed information.
        """
        return {
            "name": "get_kb_document",
            "description": "Retrieve the full content of a specific Knowledge Base document by its ID or title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The ID or title of the document to retrieve"
                    }
                },
                "required": ["document_id"]
            }
        }
    
    @staticmethod
    def get_kb_stats() -> Dict[str, Any]:
        """
        Function definition for getting KB statistics.
        
        Use this to provide information about what's in the KB.
        """
        return {
            "name": "get_kb_stats",
            "description": "Get statistics about the Knowledge Base, including number of documents, collections, and indexed status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection": {
                        "type": "string",
                        "description": "Optional: Get stats for a specific collection. Leave empty for overall stats."
                    }
                },
                "required": []
            }
        }
    
    # ==================== Phase 2: Data Extraction Functions ====================
    
    @staticmethod
    def extract_code_snippet() -> Dict[str, Any]:
        """
        Function definition for extracting and storing code snippets.
        
        Use this to extract code from the conversation and store it
        with metadata for later reference.
        """
        return {
            "name": "extract_code_snippet",
            "description": "Extract a code snippet from the conversation and save it with metadata. Useful for storing example code for later reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Programming language (e.g., 'python', '6502_asm', 'javascript')"
                    },
                    "title": {
                        "type": "string",
                        "description": "Short title for the code snippet"
                    },
                    "code": {
                        "type": "string",
                        "description": "The actual code content"
                    },
                    "description": {
                        "type": "string",
                        "description": "Explanation of what the code does"
                    }
                },
                "required": ["language", "title", "code"]
            }
        }
    
    @staticmethod
    def create_summary() -> Dict[str, Any]:
        """
        Function definition for creating structured summaries.
        
        Use this to extract key points from conversations and
        organize them in a structured format.
        """
        return {
            "name": "create_summary",
            "description": "Create a structured summary of a topic discussed in the conversation. Useful for creating study materials or reference guides.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The main topic being summarized"
                    },
                    "key_points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of key points or concepts"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Detailed explanation of the topic"
                    }
                },
                "required": ["topic", "key_points"]
            }
        }


class FunctionExecutor:
    """
    Handles the execution of functions that the LLM calls.
    
    This maps function names to actual Python implementations and
    handles the logic for each function.
    """
    
    def __init__(self, kb_manager=None, semantic_search_index=None):
        """
        Initialize the executor with references to app components.
        
        Args:
            kb_manager: KnowledgeBase instance for KB operations
            semantic_search_index: EmbeddingIndex instance for searching
        """
        self.kb_manager = kb_manager
        self.semantic_search_index = semantic_search_index
        
        # Storage for extracted data
        self.code_snippets = []
        self.summaries = []
        
        self._load_storage()
    
    def _load_storage(self):
        """Load previously saved code snippets and summaries"""
        import os
        
        self.snippets_file = "function_calling/code_snippets.json"
        self.summaries_file = "function_calling/summaries.json"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.snippets_file) or ".", exist_ok=True)
        
        # Load existing data
        if os.path.exists(self.snippets_file):
            try:
                with open(self.snippets_file, 'r') as f:
                    self.code_snippets = json.load(f)
            except:
                self.code_snippets = []
        
        if os.path.exists(self.summaries_file):
            try:
                with open(self.summaries_file, 'r') as f:
                    self.summaries = json.load(f)
            except:
                self.summaries = []
    
    def _save_storage(self):
        """Save code snippets and summaries to files"""
        with open(self.snippets_file, 'w') as f:
            json.dump(self.code_snippets, f, indent=2)
        
        with open(self.summaries_file, 'w') as f:
            json.dump(self.summaries, f, indent=2)
    
    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a function based on the LLM's request.
        
        Args:
            function_name: Name of the function to execute
            arguments: Dictionary of arguments for the function
        
        Returns:
            String result to send back to the LLM
        """
        print(f"\n[FUNCTION CALL] Executing: {function_name}")
        print(f"[FUNCTION CALL] Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            if function_name == "search_knowledge_base":
                return self._search_knowledge_base(**arguments)
            
            elif function_name == "get_kb_document":
                return self._get_kb_document(**arguments)
            
            elif function_name == "get_kb_stats":
                return self._get_kb_stats(**arguments)
            
            elif function_name == "extract_code_snippet":
                return self._extract_code_snippet(**arguments)
            
            elif function_name == "create_summary":
                return self._create_summary(**arguments)
            
            else:
                return f"Error: Unknown function '{function_name}'"
        
        except Exception as e:
            error_msg = f"Error executing {function_name}: {str(e)}"
            print(f"[FUNCTION CALL] {error_msg}")
            return error_msg
    
    # ==================== Phase 1: KB Query Implementations ====================
    
    def _search_knowledge_base(self, query: str, collection: str = None) -> str:
        """
        Search the Knowledge Base for relevant documents.
        
        This uses the semantic search index to find documents matching the query.
        """
        if not self.semantic_search_index:
            return "Error: Semantic search not available"
        
        try:
            # Search KB documents only
            results = self.semantic_search_index.search_kb_only(
                query=query,
                top_k=3,
                similarity_threshold=0.15
            )
            
            if not results:
                return f"No KB documents found matching '{query}'"
            
            # Format results for the LLM
            response = f"Found {len(results)} KB documents matching '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"{i}. **{result.get('doc_title', 'Unknown')}**\n"
                response += f"   Relevance: {result.get('similarity_score', 0)*100:.1f}%\n"
                response += f"   Preview: {result.get('text', '')[:200]}...\n\n"
            
            return response
        
        except Exception as e:
            return f"Error searching KB: {str(e)}"
    
    def _get_kb_document(self, document_id: str) -> str:
        """
        Retrieve the full content of a KB document.
        """
        if not self.kb_manager:
            return "Error: KB Manager not available"
        
        try:
            # Search for document by title or ID
            documents = self.kb_manager.list_documents()
            
            for doc in documents:
                if doc['id'] == document_id or doc['title'].lower() == document_id.lower():
                    # Combine all chunks
                    full_text = "\n\n".join([chunk['text'] for chunk in doc.get('chunks', [])])
                    
                    response = f"**{doc['title']}** (Collection: {doc['collection']})\n\n"
                    response += f"Word Count: {doc['total_words']}\n"
                    response += f"Chunks: {len(doc.get('chunks', []))}\n\n"
                    response += "Content:\n"
                    response += full_text
                    
                    return response
            
            return f"Document '{document_id}' not found in Knowledge Base"
        
        except Exception as e:
            return f"Error retrieving document: {str(e)}"
    
    def _get_kb_stats(self, collection: str = None) -> str:
        """
        Get statistics about the Knowledge Base.
        """
        if not self.kb_manager:
            return "Error: KB Manager not available"
        
        try:
            if collection:
                stats = self.kb_manager.get_collection_stats(collection)
                response = f"**{collection} Collection Statistics:**\n\n"
                response += f"Documents: {stats.get('document_count', 0)}\n"
                response += f"Total Chunks: {stats.get('total_chunks', 0)}\n"
                response += f"Total Words: {stats.get('total_words', 0)}\n"
            else:
                stats = self.kb_manager.get_stats()
                response = "**Knowledge Base Statistics:**\n\n"
                response += f"Collections: {stats.get('collection_count', 0)}\n"
                response += f"Documents: {stats.get('document_count', 0)}\n"
                response += f"Total Chunks: {stats.get('total_chunks', 0)}\n"
                response += f"Total Words: {stats.get('total_words', 0)}\n"
            
            return response
        
        except Exception as e:
            return f"Error getting KB stats: {str(e)}"
    
    # ==================== Phase 2: Data Extraction Implementations ====================
    
    def _extract_code_snippet(self, language: str, title: str, code: str, description: str = "") -> str:
        """
        Extract and store a code snippet.
        """
        try:
            snippet = {
                "id": f"snippet_{len(self.code_snippets)}_{int(datetime.now().timestamp())}",
                "language": language,
                "title": title,
                "code": code,
                "description": description,
                "created_at": datetime.now().isoformat()
            }
            
            self.code_snippets.append(snippet)
            self._save_storage()
            
            response = f"[+] Code snippet stored: '{title}' ({language})\n"
            response += f"Snippet ID: {snippet['id']}\n"
            response += f"Total snippets saved: {len(self.code_snippets)}"
            
            return response
        
        except Exception as e:
            return f"Error extracting code snippet: {str(e)}"
    
    def _create_summary(self, topic: str, key_points: List[str], explanation: str = "") -> str:
        """
        Create and store a structured summary.
        """
        try:
            summary = {
                "id": f"summary_{len(self.summaries)}_{int(datetime.now().timestamp())}",
                "topic": topic,
                "key_points": key_points,
                "explanation": explanation,
                "created_at": datetime.now().isoformat()
            }
            
            self.summaries.append(summary)
            self._save_storage()
            
            response = f"[+] Summary created: '{topic}'\n"
            response += f"Key Points: {len(key_points)}\n"
            response += f"Summary ID: {summary['id']}\n"
            response += f"Total summaries saved: {len(self.summaries)}"
            
            return response
        
        except Exception as e:
            return f"Error creating summary: {str(e)}"
    
    def get_available_functions(self) -> Dict[str, Callable]:
        """
        Return a mapping of function names to their Python implementations.
        
        This is used to look up which Python function to call based on
        the function name the LLM provides.
        """
        return {
            "search_knowledge_base": self._search_knowledge_base,
            "get_kb_document": self._get_kb_document,
            "get_kb_stats": self._get_kb_stats,
            "extract_code_snippet": self._extract_code_snippet,
            "create_summary": self._create_summary,
        }
    
    def list_code_snippets(self) -> List[Dict[str, Any]]:
        """List all saved code snippets"""
        return self.code_snippets
    
    def list_summaries(self) -> List[Dict[str, Any]]:
        """List all saved summaries"""
        return self.summaries

