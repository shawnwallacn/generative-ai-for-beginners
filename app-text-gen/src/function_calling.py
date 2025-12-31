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
            FunctionDefinitions.search_local_kb(),
            FunctionDefinitions.search_enterprise_kb(),
            FunctionDefinitions.get_kb_document(),
            FunctionDefinitions.get_kb_stats(),
            FunctionDefinitions.extract_code_snippet(),
            FunctionDefinitions.create_summary(),
        ]
    
    # ==================== Phase 1: KB Query Functions ====================
    
    @staticmethod
    def search_knowledge_base() -> Dict[str, Any]:
        """
        DEPRECATED: Use search_local_kb or search_enterprise_kb instead.
        
        Legacy function for searching the Knowledge Base.
        This function is kept for backwards compatibility only.
        New implementations should use the more specific search functions.
        """
        return {
            "name": "search_knowledge_base",
            "description": "[DEPRECATED - Use search_local_kb or search_enterprise_kb instead] Search the Knowledge Base for relevant documents. This is a legacy function kept for backwards compatibility.",
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
    def search_local_kb() -> Dict[str, Any]:
        """
        Function definition for fast local Knowledge Base search.
        
        Best for: Quick searches, testing, when you need instant results.
        """
        return {
            "name": "search_local_kb",
            "description": "Search local Knowledge Base instantly using embeddings. Fast, no API calls, perfect for quick lookups and testing. Returns results from local storage only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What you're looking for (e.g., '6502 assembly programming', 'microprocessor architecture')"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "How many results to return (default: 5, max: 10)",
                        "default": 5
                    },
                    "collection": {
                        "type": "string",
                        "description": "Optional: Search in a specific collection only (e.g., '6502-docs')"
                    }
                },
                "required": ["query"]
            }
        }
    
    @staticmethod
    def search_enterprise_kb() -> Dict[str, Any]:
        """
        Function definition for enterprise-scale Knowledge Base search.
        
        Best for: Comprehensive results, production deployments, when you need everything.
        """
        return {
            "name": "search_enterprise_kb",
            "description": "Search all knowledge sources using AI embeddings. Searches both local storage AND Azure Cosmos DB cloud database. Returns comprehensive results from all available sources. Ideal for production and when you need everything. Shows source for each result (Local or Cloud).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What you're searching for (e.g., 'complete 6502 documentation', 'all microprocessor info')"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "How many results to return (default: 5, max: 20)",
                        "default": 5
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
        
        # Filter out internal metadata before passing to functions
        clean_args = {k: v for k, v in arguments.items() if not k.startswith('_')}
        
        try:
            if function_name == "search_knowledge_base":
                # Legacy support - route to search_local_kb
                return self._search_local_kb(**clean_args)
            
            elif function_name == "search_local_kb":
                return self._search_local_kb(**clean_args)
            
            elif function_name == "search_enterprise_kb":
                return self._search_enterprise_kb(**clean_args)
            
            elif function_name == "get_kb_document":
                return self._get_kb_document(**clean_args)
            
            elif function_name == "get_kb_stats":
                return self._get_kb_stats(**clean_args)
            
            elif function_name == "extract_code_snippet":
                return self._extract_code_snippet(**clean_args)
            
            elif function_name == "create_summary":
                return self._create_summary(**clean_args)
            
            else:
                return f"Error: Unknown function '{function_name}'"
        
        except Exception as e:
            error_msg = f"Error executing {function_name}: {str(e)}"
            print(f"[FUNCTION CALL] {error_msg}")
            return error_msg
    
    # ==================== Phase 1: KB Query Implementations ====================
    
    def _search_knowledge_base(self, query: str, collection: str = None) -> str:
        """
        Legacy implementation - kept for backwards compatibility.
        Routes to _search_local_kb
        """
        return self._search_local_kb(query=query, top_k=3, collection=collection)
    
    def _search_local_kb(self, query: str, top_k: int = 5, collection: str = None) -> str:
        """
        Search the local Knowledge Base using embeddings (fast, local).
        
        This is the primary fast search function - no API calls, instant results.
        """
        if not self.semantic_search_index:
            return "Error: Local KB search not available"
        
        try:
            # Search KB documents only
            results = self.semantic_search_index.search_kb_only(
                query=query,
                top_k=top_k,
                similarity_threshold=0.15
            )
            
            if not results:
                return f"No local KB documents found matching '{query}'"
            
            # Format results for the LLM with source label
            response = f"[LOCAL KB SEARCH] Found {len(results)} documents:\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"{i}. **{result.get('doc_title', 'Unknown')}** (Local)\n"
                response += f"   Relevance: {result.get('similarity_score', 0)*100:.1f}%\n"
                response += f"   Collection: {result.get('collection_id', 'Unknown')}\n"
                response += f"   Preview: {result.get('text', '')[:200]}...\n\n"
            
            return response
        
        except Exception as e:
            return f"Error searching local KB: {str(e)}"
    
    def _search_enterprise_kb(self, query: str, top_k: int = 5) -> str:
        """
        Search Knowledge Base using Cosmos DB with embeddings (enterprise).
        
        Performs dual-source search across local KB and Azure Cosmos DB.
        This is the comprehensive search function for production deployments.
        """
        if not self.kb_manager:
            return "Error: KB Manager not available for enterprise search"
        
        try:
            from embedding_generator import EmbeddingGenerator
            
            # Initialize embedding generator
            embedding_gen = EmbeddingGenerator()
            
            if not embedding_gen.is_available():
                return "Error: Embedding generator not available. Ensure AZURE_OPENAI_API_KEY is set."
            
            # Generate query embedding
            query_embedding = embedding_gen.generate_embedding(query)
            
            if not query_embedding:
                return "Error: Failed to generate query embedding."
            
            # Perform dual-source search
            if hasattr(self.kb_manager, 'search_dual_source'):
                results = self.kb_manager.search_dual_source(
                    query=query,
                    query_embedding=query_embedding,
                    top_k=top_k
                )
            else:
                return "Error: Dual-source search not available in KB Manager"
            
            if not results:
                return f"No documents found in knowledge base matching '{query}'"
            
            # Format results for the LLM with source information
            response = f"[ENTERPRISE KB SEARCH] Found {len(results)} results from all sources:\n\n"
            
            for i, result in enumerate(results, 1):
                source = result.get('source', 'Unknown')
                similarity = result.get('similarity', 0)
                sim_pct = similarity * 100 if isinstance(similarity, float) else similarity
                
                response += f"{i}. **{result.get('title', 'Unknown')}** [{source}]\n"
                response += f"   Relevance: {sim_pct:.1f}%\n"
                response += f"   Collection: {result.get('collection_id', 'Unknown')}\n"
                response += f"   Preview: {result.get('text', '')[:200]}...\n\n"
            
            return response
        
        except Exception as e:
            return f"Error searching enterprise KB: {str(e)}"
    
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
            "search_knowledge_base": self._search_knowledge_base,  # Legacy
            "search_local_kb": self._search_local_kb,  # New
            "search_enterprise_kb": self._search_enterprise_kb,  # New
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


class AgentPlanner:
    """
    Parses and validates multi-step plans from LLM responses.
    
    The LLM can return a PLAN: section indicating multiple steps needed.
    This class extracts, parses, and validates those plans.
    
    Plan Format:
    PLAN:
    Step 1: search_enterprise_kb with query='6502 assembly'
    Step 2: extract_code_snippet from results
    Step 3: create_summary of findings
    """
    
    def __init__(self):
        """Initialize the planner"""
        pass
    
    def parse_plan_from_llm(self, llm_response: str) -> Optional[List[Dict[str, Any]]]:
        """
        Extract and parse plan from LLM response.
        
        Args:
            llm_response: Full LLM response that may contain a PLAN: section
            
        Returns:
            List of step dictionaries or None if no plan found
            
        Example:
            Input: "I'll help you. PLAN:\nStep 1: search_enterprise_kb with query='6502'"
            Output: [
                {
                    'step': 1,
                    'function': 'search_enterprise_kb',
                    'args': {'query': '6502'},
                    'depends_on': []
                }
            ]
        """
        if "PLAN:" not in llm_response:
            return None
        
        try:
            # Extract the PLAN section
            plan_section = llm_response.split("PLAN:")[1]
            lines = plan_section.strip().split("\n")
            
            steps = []
            for line in lines:
                line = line.strip()
                if not line or not line.startswith("Step"):
                    continue
                
                # Parse: "Step 1: search_enterprise_kb with query='6502'"
                # or: "Step 2: extract_code_snippet from results"
                try:
                    step_num = int(line.split(":")[0].replace("Step", "").strip())
                    rest = ":".join(line.split(":")[1:]).strip()
                    
                    # Extract function name and args
                    if " with " in rest:
                        func_part, args_part = rest.split(" with ", 1)
                        function_name = func_part.strip()
                        args = self._parse_arguments(args_part)
                    else:
                        function_name = rest.split(" from ")[0].strip() if " from " in rest else rest.strip()
                        args = {}
                    
                    step = {
                        'step': step_num,
                        'function': function_name,
                        'args': args,
                        'depends_on': self._extract_dependencies(line, step_num)
                    }
                    steps.append(step)
                
                except (ValueError, IndexError) as e:
                    print(f"[WARNING] Failed to parse step line: {line} - {e}")
                    continue
            
            return steps if steps else None
        
        except Exception as e:
            print(f"[ERROR] Failed to parse plan: {e}")
            return None
    
    def _parse_arguments(self, args_str: str) -> Dict[str, Any]:
        """
        Parse argument string into dictionary.
        
        Examples:
        "query='6502'" → {'query': '6502'}
        "language='python', title='example'" → {'language': 'python', 'title': 'example'}
        """
        args = {}
        # Simple parser for key='value' format
        import re
        matches = re.findall(r"(\w+)='([^']*)'", args_str)
        for key, value in matches:
            args[key] = value
        return args
    
    def _extract_dependencies(self, line: str, current_step: int) -> List[int]:
        """
        Extract which steps the current step depends on.
        
        Examples:
        "from results" or "from step 1 results" → [1]
        "combining all results" → [1, 2, ...] (depends on all previous)
        """
        import re
        depends = []
        
        # Look for "from step N"
        matches = re.findall(r"from step (\d+)", line, re.IGNORECASE)
        if matches:
            depends = [int(m) for m in matches]
        
        # Look for "from results" or "combining" (implicit: all previous steps)
        if ("from results" in line.lower() or "combining" in line.lower()) and not depends:
            depends = list(range(1, current_step))
        
        return depends
    
    def validate_plan(self, plan: List[Dict[str, Any]], 
                     available_functions: List[str]) -> tuple[bool, str]:
        """
        Validate that plan is executable.
        
        Checks:
        1. All functions exist
        2. Dependencies are valid (depend on earlier steps)
        3. Step numbers are sequential
        
        Returns:
            (is_valid, error_message)
        """
        if not plan:
            return False, "Empty plan"
        
        # Check sequential step numbers
        for i, step in enumerate(plan, 1):
            if step['step'] != i:
                return False, f"Steps not sequential: expected {i}, got {step['step']}"
        
        # Check all functions exist
        for step in plan:
            if step['function'] not in available_functions:
                return False, f"Unknown function: {step['function']}"
        
        # Check dependencies
        for step in plan:
            for dep in step['depends_on']:
                if dep >= step['step']:
                    return False, f"Step {step['step']} depends on later step {dep}"
                if dep < 1:
                    return False, f"Step {step['step']} has invalid dependency {dep}"
        
        return True, "Valid plan"


class PlanExecutor:
    """
    Executes multi-step plans with result chaining.
    
    Executes each step sequentially, passing results to dependent steps.
    Handles failures gracefully with partial results.
    """
    
    def __init__(self, executor: FunctionExecutor):
        """
        Initialize executor with a FunctionExecutor instance.
        
        Args:
            executor: FunctionExecutor instance for function calls
        """
        self.executor = executor
        self.results = {}  # {step_num: result}
    
    def execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multi-step plan and return results.
        
        Args:
            plan: List of step dictionaries from AgentPlanner
            
        Returns:
            {
                'success': bool,
                'steps': [
                    {'step': 1, 'function': 'search_enterprise_kb', 'result': '...', 'error': None},
                    ...
                ],
                'final_response': 'Combined results'
            }
        """
        self.results = {}
        steps_executed = []
        
        print(f"\n[AGENT PLANNER] Executing {len(plan)} steps...")
        
        for step in plan:
            step_num = step['step']
            function_name = step['function']
            args = step['args'].copy()
            depends_on = step['depends_on']
            
            print(f"\n[STEP {step_num}] Executing: {function_name}")
            
            try:
                # Inject previous results into arguments
                enriched_args = self._inject_previous_results(args, depends_on)
                
                print(f"[STEP {step_num}] Arguments: {json.dumps(enriched_args, indent=2)}")
                
                # Execute the function
                result = self.executor.execute_function(function_name, enriched_args)
                
                # Store result
                self.results[step_num] = result
                
                steps_executed.append({
                    'step': step_num,
                    'function': function_name,
                    'result': result,
                    'error': None
                })
                
                print(f"[STEP {step_num}] Success - Preview: {result[:100]}...")
            
            except Exception as e:
                error_msg = f"Step {step_num} failed: {str(e)}"
                print(f"[ERROR] {error_msg}")
                
                steps_executed.append({
                    'step': step_num,
                    'function': function_name,
                    'result': None,
                    'error': error_msg
                })
                
                # Continue execution to get partial results
                # (could also fail-fast here if preferred)
        
        # Check if all steps succeeded
        success = all(step['error'] is None for step in steps_executed)
        
        # Generate final response
        final_response = self._generate_final_response(steps_executed)
        
        return {
            'success': success,
            'steps': steps_executed,
            'final_response': final_response,
            'total_steps': len(plan),
            'completed_steps': sum(1 for s in steps_executed if s['error'] is None)
        }
    
    def _inject_previous_results(self, args: Dict[str, Any], 
                                depends_on: List[int]) -> Dict[str, Any]:
        """
        Inject previous step results into current step arguments.
        
        For example, if Step 2 depends on Step 1 results:
        - Take Step 1 result
        - Add a '_previous_results' key to args
        - Function implementation can use this
        
        Note: _previous_results is metadata, not passed to actual function
        """
        if not depends_on:
            return args
        
        enriched_args = args.copy()
        
        # Collect all previous results
        previous_results = {}
        for dep_step in depends_on:
            if dep_step in self.results:
                previous_results[f'step_{dep_step}'] = self.results[dep_step]
        
        # Add to args (functions can check for _previous_results)
        # This is metadata that functions can optionally use
        if previous_results:
            enriched_args['_context'] = {
                'previous_results': previous_results,
                'dependency_steps': depends_on
            }
        
        return enriched_args
    
    def _generate_final_response(self, steps: List[Dict[str, Any]]) -> str:
        """
        Generate a natural language summary of the plan execution.
        """
        if not steps:
            return "No steps executed."
        
        successful_steps = [s for s in steps if s['error'] is None]
        failed_steps = [s for s in steps if s['error'] is not None]
        
        response = f"\n[MULTI-STEP EXECUTION SUMMARY]\n"
        response += f"Total Steps: {len(steps)}\n"
        response += f"Successful: {len(successful_steps)}\n"
        response += f"Failed: {len(failed_steps)}\n\n"
        
        if successful_steps:
            response += "Results:\n"
            for step in successful_steps:
                result_preview = step['result'][:150] if step['result'] else "No result"
                response += f"\nStep {step['step']} ({step['function']}):\n{result_preview}...\n"
        
        if failed_steps:
            response += "\nErrors:\n"
            for step in failed_steps:
                response += f"Step {step['step']}: {step['error']}\n"
        
        return response
