import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.tools import tool
from firecrawl import Firecrawl
from model import get_langchain_embedding_engine
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

load_dotenv()

# Rich console for beautiful output
console = Console()

# Global vector store that persists across tool calls
vectorstore = None
embedding_engine = None


def get_or_create_vectorstore(api_key: str = None):
    """Get existing vector store or create a new one"""
    global vectorstore, embedding_engine

    if vectorstore is None:
        try:
            if embedding_engine is None or api_key:
                console.print("🔧 Creating embedding engine...", style="blue")
                embedding_engine = get_langchain_embedding_engine(api_key)
                console.print("✅ Embedding engine created successfully", style="green")

            vectorstore = InMemoryVectorStore(embedding_engine)
            console.print("🆕 Created new vector store instance", style="blue")
        except Exception as e:
            console.print(f"❌ Error creating vector store: {str(e)}", style="red")
            raise e

    return vectorstore


def initialize_vectorstore_with_cv(cv_path: str, api_key: str = None):
    """Initialize the global vector store with CV content"""
    global vectorstore

    try:
        # Check if file exists
        if not Path(cv_path).exists():
            console.print(f"❌ Error: CV file '{cv_path}' not found.", style="red")
            return False

        console.print(f"📖 Loading CV: {cv_path}", style="blue")

        # Load PDF
        loader = PyPDFLoader(cv_path)
        documents = loader.load()

        if not documents:
            console.print("❌ Error: No content found in CV.", style="red")
            return False

        console.print(f"📄 Found {len(documents)} pages", style="green")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        console.print(f"✂️  Split into {len(chunks)} chunks", style="green")

        # Get or create vector store and add documents
        console.print("🧠 Creating embeddings...", style="yellow")
        try:
            vs = get_or_create_vectorstore(api_key)
        except Exception as e:
            console.print(f"❌ Failed to create vector store: {str(e)}", style="red")
            return False

        # Clear existing documents by creating a new instance
        if vectorstore is not None:
            console.print("🗑️  Clearing existing documents...", style="yellow")
            # Create a fresh vector store instance
            try:
                vectorstore = InMemoryVectorStore(embedding_engine)
                vs = vectorstore
            except Exception as e:
                console.print(
                    f"❌ Failed to recreate vector store: {str(e)}", style="red"
                )
                return False

        # Add all chunks to the vector store
        console.print(
            f"📝 Adding {len(chunks)} chunks to vector store...", style="blue"
        )
        try:
            vs.add_documents(chunks)
            console.print("✅ Documents added successfully", style="green")
        except Exception as e:
            console.print(f"❌ Failed to add documents: {str(e)}", style="red")
            return False

        return True

    except Exception as e:
        console.print(f"❌ Error loading CV: {str(e)}", style="red")
        return False


def create_tools_with_api_keys(google_api_key: str, firecrawl_api_key: str):
    """Create tools with the provided API keys"""

    @tool
    def kb_tool(query: str):
        """
        Search the knowledgebase (CV) for relevant content.

        Args:
            query: The search query to find relevant content in your CV

        Returns:
            Relevant content from your CV that matches the query
        """
        global vectorstore

        if vectorstore is None:
            return "❌ CV knowledge base not initialized. Please initialize with your CV first."

        # Search for relevant content in CV
        try:
            relevant_docs = vectorstore.similarity_search(query, k=10)

            if not relevant_docs:
                return "No relevant content found in your CV for this query."

            return relevant_docs

        except Exception as e:
            return f"## ❌ Error\n\nError searching CV: {str(e)}"

    @tool
    def load_pdf_and_create_embeddings(pdf_path: str):
        """Load PDF and create embeddings in memory"""
        return initialize_vectorstore_with_cv(pdf_path, google_api_key)

    @tool
    def crawl_website(url: str):
        """
        Crawl a website and return the content.

        Args:
            url: The URL of the website to crawl

        Returns:
            The content of the website
        """
        if not firecrawl_api_key:
            return "❌ Firecrawl API key is required for web crawling."

        firecrawl = Firecrawl(api_key=firecrawl_api_key)

        try:
            console.print(f"🔥 Crawling website: {url}", style="yellow")
            docs = firecrawl.crawl(url=url, limit=10)

            if docs:
                return docs
            else:
                return "## 🌐 Website Crawl Results\n\nNo content found on the website."

        except Exception as e:
            return f"## ❌ Error\n\nError crawling website: {str(e)}"

    return [kb_tool, load_pdf_and_create_embeddings, crawl_website]


# Legacy tools for backward compatibility
@tool
def kb_tool(query: str):
    """
    Search the knowledgebase (CV) for relevant content.

    Args:
        query: The search query to find relevant content in your CV

    Returns:
        Relevant content from your CV that matches the query
    """
    global vectorstore

    if vectorstore is None:
        return "❌ CV knowledge base not initialized. Please initialize with your CV first."

    # Search for relevant content in CV
    try:
        relevant_docs = vectorstore.similarity_search(query, k=10)

        if not relevant_docs:
            return "No relevant content found in your CV for this query."

        return relevant_docs

    except Exception as e:
        return f"## ❌ Error\n\nError searching CV: {str(e)}"


@tool
def load_pdf_and_create_embeddings(pdf_path: str):
    """Load PDF and create embeddings in memory (legacy tool, use initialize_vectorstore_with_cv instead)"""
    return initialize_vectorstore_with_cv(pdf_path)


@tool
def crawl_website(url: str, api_key: str):
    """
    Crawl a website and return the content.

    Args:
        url: The URL of the website to crawl

    Returns:
        The content of the website
    """
    firecrawl = Firecrawl(api_key=api_key)

    try:
        console.print(f"🔥 Crawling website: {url}", style="yellow")
        docs = firecrawl.crawl(url=url, limit=10)

        if docs:
            return docs
        else:
            return "## 🌐 Website Crawl Results\n\nNo content found on the website."

    except Exception as e:
        return f"## ❌ Error\n\nError crawling website: {str(e)}"


# Default tools list (will be overridden by create_tools_with_api_keys in agent.py)
TOOLS = [kb_tool, initialize_vectorstore_with_cv, crawl_website]
