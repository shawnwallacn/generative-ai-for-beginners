"""
UX Improvements Module for Better User Experience

This module provides:
1. Better error messages with helpful guidance
2. Response transparency (source indicators)
3. Confidence/relevance scores
4. Helpful tips and suggestions
5. Privacy and data control
"""

import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ErrorMessages:
    """Friendly error messages with helpful suggestions"""
    
    @staticmethod
    def invalid_command(user_input: str) -> str:
        """Handle unrecognized commands with suggestions"""
        return f"""
I didn't recognize '{user_input}' as a command. 

Popular commands to try:
  • help          → See ALL available commands
  • model         → Change AI model
  • prompt        → View/customize system prompt
  • kb-search     → Search your Knowledge Base
  • params        → Adjust model parameters
  • privacy       → Privacy and data settings

Type 'help' anytime to see what you can do! 🚀
"""

    @staticmethod
    def empty_input() -> str:
        """Handle empty input"""
        return """
Please enter a prompt or command. Here are some ideas:

Examples:
  • Ask a question: "What is machine learning?"
  • Search KB: "Search for 6502 assembly"
  • Extract code: "Show me a Python example and save it"
  • Get stats: "Show me usage statistics"
  • View help: "help"

What would you like to do? 💡
"""

    @staticmethod
    def file_not_found(filename: str) -> str:
        """Handle missing files gracefully"""
        return f"""
Couldn't find '{filename}'. 

This could happen if:
  • The file was deleted
  • You haven't created one yet
  • The path is incorrect

Try:
  • 'load' to see available saved conversations
  • 'batch' to manage batch jobs
  • 'kb' to view Knowledge Base

Need help? Type 'help'
"""

    @staticmethod
    def kb_empty() -> str:
        """Handle empty Knowledge Base"""
        return """
Your Knowledge Base is empty. Let's get started!

You can:
  1. Type 'kb' to create a new collection
  2. Add documents (TXT, Markdown, or PDF)
  3. Index them with 'index-kb'
  4. Search with 'kb-search'

Example:
  • Create collection: 'kb' → Option 1
  • Add document: 'kb' → Option 2
  • Index: 'index-kb'
  • Search: 'kb-search' then ask your question

Your KB enables smarter responses! 📚
"""

    @staticmethod
    def no_conversations_saved() -> str:
        """Handle no saved conversations"""
        return """
You haven't saved any conversations yet.

To save a conversation:
  1. Have a conversation with the AI
  2. Type 'save' to save it
  3. Give it a name when prompted
  4. Load it anytime with 'load'

Saved conversations help with:
  • Continuing important discussions
  • Keeping research organized
  • Building on previous insights
"""

    @staticmethod
    def no_snippets_extracted() -> str:
        """Handle no code snippets"""
        return """
You haven't extracted any code snippets yet.

To extract code:
  1. Ask the AI for code: "Show me a Python example"
  2. Ask to save it: "Save this as a code snippet"
  3. View them anytime: type 'fc-snippets'

Examples:
  • "Show me a 6502 LDA instruction and save it"
  • "Create a Python function and extract it"
  • "Save that assembly code"
"""

    @staticmethod
    def no_summaries_created() -> str:
        """Handle no summaries"""
        return """
You haven't created any summaries yet.

To create a summary:
  1. Ask the AI to summarize: "Create a summary of 6502"
  2. View them anytime: type 'fc-summaries'

Examples:
  • "Create a summary of machine learning basics"
  • "Summarize the 6502 instruction set with key points"
  • "Generate study notes on assembly programming"

Perfect for study materials! 📖
"""

    @staticmethod
    def api_error() -> str:
        """Handle API errors gracefully"""
        return """
Oops! There was an issue connecting to the AI service.

This could be due to:
  • Network connectivity issues
  • API rate limiting
  • Temporary service outage
  • Invalid API key in .env file

Troubleshooting:
  1. Check your internet connection
  2. Wait a moment and try again
  3. Check your .env file for GITHUB_TOKEN
  4. Try a different model with 'model'

Need help? Check your .env configuration 🔧
"""


class ResponseTransparency:
    """Show users where responses come from"""
    
    @staticmethod
    def show_source_indicator(has_kb: bool, has_rag: bool, 
                             similarity_score: Optional[float] = None) -> str:
        """Display where the response is coming from"""
        sources = []
        
        if has_kb:
            sources.append("📚 KB")
        if has_rag:
            conf = ResponseTransparency.confidence_level(similarity_score)
            sources.append(f"🔍 Context {conf}")
        if not has_kb and not has_rag:
            sources.append("🧠 Training Data")
        
        return f"[{' + '.join(sources)}] "
    
    @staticmethod
    def confidence_level(score: Optional[float]) -> str:
        """Convert similarity score to user-friendly confidence"""
        if score is None:
            return "(Medium confidence)"
        
        percentage = int(score * 100)
        
        if percentage >= 80:
            return f"(High {percentage}%)"
        elif percentage >= 50:
            return f"(Medium {percentage}%)"
        else:
            return f"(Low {percentage}%)"
    
    @staticmethod
    def explain_function_call(function_name: str) -> str:
        """Explain what function was called and why"""
        explanations = {
            "search_knowledge_base": "🔎 Searching your Knowledge Base for relevant documents...",
            "get_kb_document": "📖 Retrieving full document from Knowledge Base...",
            "get_kb_stats": "📊 Getting Knowledge Base statistics...",
            "extract_code_snippet": "💾 Extracting and saving code for later reference...",
            "create_summary": "✨ Creating a structured summary of the discussion...",
        }
        
        return explanations.get(function_name, f"🔧 Using {function_name}...")


class HelpfulTips:
    """Suggest useful features to users"""
    
    TIPS = [
        "💡 Tip: Use 'params' to tune model temperature for more creative or precise responses",
        "💡 Tip: Use 'rag' to enable context-aware responses from your conversation history",
        "💡 Tip: Use 'kb' to create a Knowledge Base of your documents for smarter answers",
        "💡 Tip: Use 'batch' to process multiple prompts at once",
        "💡 Tip: Use 'rate' to rate responses - helps track quality over time",
        "💡 Tip: Use 'template' to pick pre-built prompts for common tasks",
        "💡 Tip: Use 'profile' to switch between different role configurations",
        "💡 Tip: Use 'export' to share conversations in Markdown, CSV, or HTML",
        "💡 Tip: Use 'analyze' to see detailed stats about your conversations",
        "💡 Tip: Use 'semantic-search' to find conversations by meaning, not just keywords",
        "💡 Tip: Use 'fc-snippets' to view all code you've extracted",
        "💡 Tip: Use 'fc-summaries' to view all summaries you've created",
        "💡 Tip: Use 'privacy' to control how your data is collected",
        "💡 Tip: Type 'help' anytime to see all available commands",
    ]
    
    @staticmethod
    def random_tip() -> str:
        """Return a random helpful tip"""
        return random.choice(HelpfulTips.TIPS)
    
    @staticmethod
    def contextual_tips(feature: str) -> List[str]:
        """Return tips relevant to a specific feature"""
        tips_map = {
            "kb": [
                "📚 Build a Knowledge Base: 'kb' → Create collection → Add documents",
                "🔎 Search your KB: 'kb-search' to find relevant documents",
                "🎯 Index for better search: 'index-kb' to enable semantic search",
            ],
            "rag": [
                "🧠 RAG uses your conversation history as context",
                "🎚️ Adjust similarity threshold: 'rag' → Change threshold",
                "🎯 Ask specific questions to get better context",
            ],
            "function_calling": [
                "🤖 The AI automatically uses tools when helpful",
                "💾 Code snippets are saved for later: 'fc-snippets'",
                "📝 Summaries help with study materials: 'fc-summaries'",
            ],
            "batch": [
                "⚡ Batch jobs save time on repetitive prompts",
                "📊 Track progress: 'batch' → View job details",
                "📥 Export results: 'batch-run' when done",
            ]
        }
        
        return tips_map.get(feature, [HelpfulTips.random_tip()])


class DataTransparency:
    """Show users what data is being collected"""
    
    @staticmethod
    def data_collection_summary() -> str:
        """Show what data is collected"""
        return """
============================================================
Data Collection Summary
============================================================

Currently being saved:
  ✓ Conversations (for history and context)
  ✓ User profiles (model and prompt preferences)
  ✓ Feedback ratings (to track quality)
  ✓ Extracted code snippets (for reference)
  ✓ Generated summaries (for study materials)
  ✓ Usage statistics (tokens, costs, models)
  ✓ Knowledge Base documents (for RAG)

All data is stored locally on your computer in:
  • conversations/ - Chat history
  • profiles/ - Your settings
  • function_calling/ - Extracted code/summaries
  • embeddings/ - Search indexes
  • knowledge_base/ - Your documents

You have full control:
  • Type 'privacy' to manage data settings
  • Delete specific conversations anytime
  • Export your data anytime
  • Turn off auto-save if you prefer

No data is sent to external servers except:
  • AI API requests (to GitHub Models / Azure OpenAI)
  • These are required for the app to work

Questions? Type 'help' or 'privacy' 🔒
"""
    
    @staticmethod
    def opt_in_consent() -> str:
        """First-time consent message"""
        return """
============================================================
Welcome to the Text Generation App! 👋
============================================================

This app will save:
  • Your conversations (for context and history)
  • Your preferences (model choice, system prompt)
  • Your feedback (ratings and flags)
  • Extracted code and summaries (for reference)

Why we save this:
  • Better AI responses using your context
  • Personalized experience for your needs
  • Search and analytics on your conversations
  • Function calling to extract and save useful content

Your privacy:
  • All data is stored locally on YOUR computer
  • No data is shared with anyone
  • You can delete anything anytime
  • Type 'privacy' to control what's saved

Ready to get started? 🚀
"""


class ConversationStarters:
    """Suggest ways to get started"""
    
    STARTERS = [
        "Ask a question: 'What is machine learning?'",
        "Code help: 'Show me a Python example'",
        "Search KB: 'Search for 6502 assembly'",
        "Extract code: 'Save this as a snippet'",
        "Get advice: 'Help me with debugging this code'",
        "Create: 'Generate a summary of 6502'",
    ]
    
    @staticmethod
    def random_starter() -> str:
        """Return a random conversation starter"""
        return random.choice(ConversationStarters.STARTERS)
    
    @staticmethod
    def feature_highlight(feature: str) -> str:
        """Highlight a specific feature"""
        highlights = {
            "kb": "💾 Save your Knowledge Base: 'kb' to get started",
            "rag": "🧠 Enable RAG: 'rag' to use conversation context",
            "semantic_search": "🔍 Search by meaning: 'semantic-search'",
            "function_calling": "🤖 Auto-extraction: The AI saves code & summaries",
            "batch": "⚡ Process multiple: 'batch' for bulk prompts",
            "profiles": "👤 Save settings: 'new-profile' to create one",
        }
        
        return highlights.get(feature, "Try a command: type 'help'")

