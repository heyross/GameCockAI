import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.text import Text
import ollama
import sys

# Import the tool-enabled Raven system
try:
    from src.rag_unified import query_raven_with_tools
    TOOL_ENABLED_RAVEN = True
    print("✅ Tool-enabled Raven system loaded")
except ImportError as e:
    print(f"⚠️ Tool-enabled Raven not available: {e}")
    TOOL_ENABLED_RAVEN = False
    try:
        from tools import TOOL_MAP
    except ImportError:
        TOOL_MAP = {}

class RAGSystem:
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        """Initialize the RAG system with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.knowledge_base = []
        self.embeddings = None
        self.console = Console()
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the knowledge base and update embeddings."""
        self.knowledge_base.extend(documents)
        # Update embeddings
        texts = [doc['content'] for doc in self.knowledge_base]
        self.embeddings = self.model.encode(texts, show_progress_bar=True) if texts else None
    
    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve the most relevant documents for a given query."""
        if not self.knowledge_base:
            return []
            
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Calculate similarity scores
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [{
            'document': self.knowledge_base[idx],
            'score': float(similarities[idx])
        } for idx in top_indices]

class ChatInterface:
    def __init__(self):
        self.console = Console()
        self.rag = RAGSystem()
        self.messages = [{
            'role': 'system',
            'content': (
                'You are Raven, an expert financial data assistant with access to 18 specialized tools. '
                'Your goal is to help users by answering questions and performing tasks using your available tools. '
                'When a user\'s request is ambiguous, ask clarifying questions to understand their intent before using your tools. '
                'Be conversational and guide the user if they seem unsure. You have access to company search, data downloading, '
                'processing, analytics, and database management tools.'
            )
        }]
        self.command_history = []
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.history_file = Path(f'chat_history_{self.session_id}.json')
        self.tool_enabled = TOOL_ENABLED_RAVEN
        
    def save_history(self):
        """Save chat history to a file."""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, indent=2)
    
    def load_knowledge_base(self, directory: str):
        """Load documents from a directory into the RAG system."""
        # TODO: Implement document loading from directory
        pass
    
    def process_query(self, query: str) -> str:
        """Process a user query and return a response."""
        # Add user message to history
        self.messages.append({'role': 'user', 'content': query})
        self.command_history.append(query)
        
        # Check for commands
        if query.startswith('/'):
            return self._handle_command(query[1:])
        
        # Use tool-enabled Raven system if available
        if self.tool_enabled:
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    task = progress.add_task("Raven is thinking and using tools...", total=None)
                    response_text = query_raven_with_tools(query, self.messages)
                
                # Add response to history
                self.messages.append({'role': 'assistant', 'content': response_text})
                
                # Save history
                self.save_history()
                
                return response_text
                
            except Exception as e:
                self.console.print(f"[red]Error with tool-enabled Raven: {e}[/red]")
                # Fall back to basic RAG
                self.tool_enabled = False
        
        # Fallback: Use basic RAG system
        context = self.rag.retrieve_relevant_documents(query)
        
        # Prepare the prompt with context
        prompt = self._build_prompt(query, context)
        
        # Get response from the model
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Thinking...", total=None)
            response = ollama.chat(
                model='raven-enhanced',
                messages=self.messages + [{'role': 'user', 'content': prompt}],
                stream=False
            )
        
        # Extract and format the response
        response_text = response['message']['content']
        self.messages.append({'role': 'assistant', 'content': response_text})
        
        # Save history
        self.save_history()
        
        return response_text
    
    def _build_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Build a prompt with relevant context."""
        prompt = f"User query: {query}\n\n"
        
        if context:
            prompt += "Relevant context:\n"
            for i, doc in enumerate(context, 1):
                prompt += f"{i}. {doc['document']['content'][:200]}... (relevance: {doc['score']:.2f})\n"
        
        prompt += "\nPlease provide a helpful response based on the above context and your knowledge."
        return prompt
    
    def _handle_command(self, command: str) -> str:
        """Handle slash commands."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        commands = {
            'help': self._cmd_help,
            'clear': self._cmd_clear,
            'history': self._cmd_history,
            'exit': self._cmd_exit,
            'load': self._cmd_load,
            'save': self._cmd_save,
            'tools': self._cmd_tools,
        }
        
        handler = commands.get(cmd, self._cmd_not_found)
        return handler(args)
    
    def _cmd_help(self, args: list) -> str:
        """Show help information."""
        help_text = """[bold]Available Commands:[/bold]\n"""
        commands = {
            '/help': 'Show this help message',
            '/clear': 'Clear the chat history',
            '/history': 'Show command history',
            '/exit': 'Exit the chat',
            '/load <file>': 'Load a knowledge base file',
            '/save [file]': 'Save the current session',
            '/tools': 'Show available tools and capabilities',
        }
        
        for cmd, desc in commands.items():
            help_text += f"[cyan]{cmd:15}[/cyan] {desc}\n"
        
        return help_text
    
    def _cmd_clear(self, args: list) -> str:
        """Clear the chat history."""
        self.messages = [self.messages[0]]  # Keep system message
        return "Chat history cleared."
    
    def _cmd_history(self, args: list) -> str:
        """Show command history."""
        if not self.command_history:
            return "No commands in history."
        return "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(self.command_history[-10:]))
    
    def _cmd_exit(self, args: list) -> str:
        """Exit the chat."""
        self.save_history()
        return "Goodbye!"
    
    def _cmd_load(self, args: list) -> str:
        """Load a knowledge base file."""
        if not args:
            return "Please specify a file to load."
        
        file_path = Path(args[0])
        if not file_path.exists():
            return f"File not found: {file_path}"
            
        try:
            # TODO: Implement document loading logic
            return f"Loaded knowledge base from {file_path}"
        except Exception as e:
            return f"Error loading file: {e}"
    
    def _cmd_save(self, args: list) -> str:
        """Save the current session."""
        save_path = args[0] if args else self.history_file
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'messages': self.messages,
                    'command_history': self.command_history,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            return f"Session saved to {save_path}"
        except Exception as e:
            return f"Error saving session: {e}"
    
    def _cmd_tools(self, args: list) -> str:
        """Show available tools and capabilities."""
        if not self.tool_enabled:
            return "❌ Tool-enabled Raven is not available. Running in basic mode."
        
        try:
            # Use the tool orchestrator to get tool information
            from src.rag_tool_orchestrator import RAGToolOrchestrator
            orchestrator = RAGToolOrchestrator()
            return orchestrator._handle_tool_help()
        except Exception as e:
            return f"❌ Error retrieving tool information: {e}"
    
    def _cmd_not_found(self, args: list) -> str:
        """Handle unknown commands."""
        return f"Unknown command. Type /help for a list of available commands."

def main():
    """Run the interactive chat interface."""
    console = Console()
    chat = ChatInterface()
    
    # Check if tool-enabled Raven is available
    tool_status = "✅ Tool-enabled" if TOOL_ENABLED_RAVEN else "⚠️ Basic mode"
    
    console.print(
        Panel(
            f"[bold blue]🖤 Welcome to Raven[/bold blue] - Your Financial Data Assistant ({tool_status})\n\n"
            f"👋 Hello! I'm Raven, your intelligent financial data assistant.\n"
            f"I have access to {len(TOOL_MAP) if 'TOOL_MAP' in globals() else '18'} specialized tools\n"
            f"to help you navigate the complex world of financial data.\n\n"
            f"[bold]💬 Let's start a conversation![/bold] Here are some things you can ask me:\n"
            f"• 'What can you help me with?' - Discover my full capabilities\n"
            f"• 'What data do you have access to?' - Explore available datasets\n"
            f"• 'Search for Apple company' - Find and analyze companies\n"
            f"• 'Show me database statistics' - See what data we have\n"
            f"• 'Analyze market trends' - Get AI-powered market insights\n\n"
            f"[dim]Type your questions or use /help for commands[/dim]",
            title="🖤 Raven's Financial Intelligence Hub",
            border_style="blue",
        )
    )
    
    try:
        while True:
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()
                if not user_input:
                    continue
                    
                if user_input.lower() in ('exit', 'quit', 'q'):
                    break
                    
                # Get and display response
                with console.status("[bold green]Thinking..."):
                    response = chat.process_query(user_input)
                
                # Print response with Markdown formatting
                console.print("\n[bold green]Raven:[/bold green]")
                console.print(Markdown(response))
                
            except KeyboardInterrupt:
                console.print("\nUse 'exit' or 'q' to quit.")
                continue
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue
                
    finally:
        chat.save_history()
        console.print("\n[bold]Chat session ended. History saved.[/bold]")

if __name__ == "__main__":
    main()
