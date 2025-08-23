import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.tools import tool
from firecrawl import Firecrawl
from model import get_embedding_engine
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

load_dotenv()

# Rich console for beautiful output
console = Console()

# Global vector store that persists across tool calls
vectorstore = None
embedding_engine = None

firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))


def get_or_create_vectorstore():
    """Get existing vector store or create a new one"""
    global vectorstore, embedding_engine

    if vectorstore is None:
        if embedding_engine is None:
            embedding_engine = get_embedding_engine()
        vectorstore = InMemoryVectorStore(embedding_engine)
        console.print("🆕 Created new vector store instance", style="blue")

    return vectorstore


def get_document_count(vectorstore):
    """Get the actual document count from the vector store"""
    try:
        # Try different methods to get document count
        if hasattr(vectorstore, "docstore") and hasattr(vectorstore.docstore, "dict"):
            return len(vectorstore.docstore.dict)
        elif hasattr(vectorstore, "_docstore") and hasattr(
            vectorstore._docstore, "dict"
        ):
            return len(vectorstore._docstore.dict)
        elif hasattr(vectorstore, "index_to_docstore_id"):
            return len(vectorstore.index_to_docstore_id)
        elif hasattr(vectorstore, "index"):
            return len(vectorstore.index)
        else:
            # Try a simple search to see if documents exist
            try:
                test_results = vectorstore.similarity_search("test", k=1)
                return len(test_results) if test_results else 0
            except:
                return 0
    except Exception as e:
        console.print(
            f"⚠️  Could not determine document count: {str(e)}", style="yellow"
        )
        return 0


def initialize_vectorstore_with_cv(cv_path: str):
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
        vs = get_or_create_vectorstore()

        # Clear existing documents by creating a new instance
        if vectorstore is not None:
            console.print("🗑️  Clearing existing documents...", style="yellow")
            # Create a fresh vector store instance
            vectorstore = InMemoryVectorStore(embedding_engine)
            vs = vectorstore

        # Add all chunks to the vector store
        console.print(
            f"📝 Adding {len(chunks)} chunks to vector store...", style="blue"
        )
        vs.add_documents(chunks)

        # Verify documents were added
        total_docs = get_document_count(vs)
        console.print(
            f"✅ CV embeddings created successfully! Total documents: {total_docs}",
            style="green",
        )

        if total_docs == 0:
            console.print(
                "⚠️  Warning: No documents were added to the vector store!", style="red"
            )
            console.print(
                "💡 This might indicate an issue with the embedding process",
                style="yellow",
            )

        return True

    except Exception as e:
        console.print(f"❌ Error loading CV: {str(e)}", style="red")
        return False


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
        relevant_docs = vectorstore.similarity_search(query, k=3)

        if not relevant_docs:
            return "No relevant content found in your CV for this query."

        # Format the response nicely with markdown
        formatted_response = []
        formatted_response.append(f"## 📄 CV Search Results for: '{query}'")
        formatted_response.append("")

        for i, doc in enumerate(relevant_docs, 1):
            formatted_response.append(f"### Result {i}")
            formatted_response.append(f"{doc.page_content}")
            formatted_response.append("")

        return "\n".join(formatted_response)

    except Exception as e:
        return f"## ❌ Error\n\nError searching CV: {str(e)}"


@tool
def load_pdf_and_create_embeddings(pdf_path: str):
    """Load PDF and create embeddings in memory (legacy tool, use initialize_vectorstore_with_cv instead)"""
    return initialize_vectorstore_with_cv(pdf_path)


@tool
def get_cv_stats():
    """Get statistics about the CV knowledge base"""
    global vectorstore

    if vectorstore is None:
        return "❌ CV knowledge base not initialized."

    try:
        total_docs = get_document_count(vectorstore)
        return f"## 📊 CV Knowledge Base Stats\n\n**Total Documents:** {total_docs}\n**Status:** {'✅ Active' if total_docs > 0 else '❌ Empty'}"
    except Exception as e:
        return f"## ❌ Error\n\nError getting stats: {str(e)}"


@tool
def crawl_website(url: str):
    """
    Crawl a website and return the content.

    Args:
        url: The URL of the website to crawl

    Returns:
        The content of the website
    """
    try:
        console.print(f"🔥 Crawling website: {url}", style="yellow")
        docs = firecrawl.crawl(url=url, limit=10)

        if docs:
            # Format the crawled content nicely with markdown
            formatted_content = []
            formatted_content.append(f"## 🌐 Website Crawl Results for: {url}")
            formatted_content.append("")

            for i, doc in enumerate(docs, 1):
                formatted_content.append(f"### Page {i}")
                if hasattr(doc, "page_content"):
                    content = (
                        doc.page_content[:500] + "..."
                        if len(doc.page_content) > 500
                        else doc.page_content
                    )
                    formatted_content.append(f"{content}")
                else:
                    formatted_content.append(f"{str(doc)}")
                formatted_content.append("")

            return "\n".join(formatted_content)
        else:
            return "## 🌐 Website Crawl Results\n\nNo content found on the website."

    except Exception as e:
        return f"## ❌ Error\n\nError crawling website: {str(e)}"


@tool
def debug_vectorstore():
    """Debug the vector store to see what's happening"""
    global vectorstore

    if vectorstore is None:
        return "❌ Vector store is None"

    debug_info = []
    debug_info.append("## 🔍 Vector Store Debug Information")
    debug_info.append("")

    try:
        # Check vector store attributes
        debug_info.append("### Vector Store Attributes:")
        debug_info.append(f"- Type: {type(vectorstore)}")
        debug_info.append(f"- Has docstore: {hasattr(vectorstore, 'docstore')}")
        debug_info.append(f"- Has _docstore: {hasattr(vectorstore, '_docstore')}")
        debug_info.append(f"- Has index: {hasattr(vectorstore, 'index')}")
        debug_info.append(
            f"- Has index_to_docstore_id: {hasattr(vectorstore, 'index_to_docstore_id')}"
        )
        debug_info.append("")

        # Try to get document count
        total_docs = get_document_count(vectorstore)
        debug_info.append(f"### Document Count: {total_docs}")
        debug_info.append("")

        # Try a test search
        debug_info.append("### Test Search Results:")
        try:
            test_results = vectorstore.similarity_search("test", k=1)
            debug_info.append(f"- Test search returned: {len(test_results)} results")
            if test_results:
                debug_info.append(
                    f"- First result content length: {len(test_results[0].page_content)}"
                )
            else:
                debug_info.append("- No results found")
        except Exception as e:
            debug_info.append(f"- Test search failed: {str(e)}")

        return "\n".join(debug_info)

    except Exception as e:
        return f"## ❌ Debug Error\n\nError during debug: {str(e)}"


TOOLS = [
    kb_tool,
    initialize_vectorstore_with_cv,
    crawl_website,
    get_cv_stats,
    debug_vectorstore,
]
