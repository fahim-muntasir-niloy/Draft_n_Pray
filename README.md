# Draft 'n' Pray

A **professional AI agent** with a beautiful CLI interface that always has access to your CV through an in-memory vector store and can crawl websites for additional information.

## ✨ Features

- **🎨 Beautiful CLI Interface**: Professional-looking terminal application with colors, progress bars, and rich formatting
- **📄 CV Knowledge Base**: Automatically loads and indexes your CV for quick access
- **🕷️ Web Crawling**: Can crawl websites to gather additional information
- **🧠 Persistent Memory**: CV embeddings are kept in memory during the session
- **💬 Interactive Chat**: Rich command-line interface with built-in commands
- **🔧 Built-in Commands**: `help`, `tools`, `cv`, `quit` for easy navigation
- **📝 Markdown Rendering**: Beautifully renders LLM responses with proper markdown formatting

## 🚀 Quick Start

### Method 1: Using Typer CLI (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with typer
python -m agent main
```

### Method 2: Direct Python execution
```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python run.py
```

### Method 3: Using the module
```bash
# Install dependencies
pip install -r requirements.txt

# Run as module
python -m agent
```

## ⚙️ Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file in the project root with:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   CV_PATH=path/to/your/cv.pdf
   ```

3. **Place your CV**:
   - Put your CV (PDF format) in the project directory, or
   - Update the `CV_PATH` in your `.env` file to point to your CV location

## 🎯 Usage

### Starting the Agent
The agent will automatically:
- ✅ Check environment configuration
- 🧠 Initialize the AI model
- 📖 Load your CV and create embeddings
- 🛠️ Display available tools
- 💬 Start the interactive chat session

### Available Commands
- **`help`** - Show help information and examples
- **`tools`** - Display available tools and their usage
- **`cv`** - Show CV status and information
- **`quit`**, **`exit`**, **`bye`** - Exit the application

### Example Interactions
```
💬 You: What are my technical skills?
🤖 Agent: [Agent searches your CV and responds with formatted markdown]

💬 You: Crawl https://example.com and tell me about it
🤖 Agent: [Agent crawls the website and provides formatted markdown response]

💬 You: help
📚 Help: [Shows available commands and examples]
```

## 🛠️ Available Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `kb_tool` | Search your CV for relevant information | Ask about your skills, experience, etc. |
| `crawl_website` | Crawl websites for content | Provide a URL to crawl |
| `initialize_vectorstore_with_cv` | Re-initialize CV knowledge base | Use if CV changes |

## 🎨 CLI Features

- **Colorful Output**: Beautiful colors and formatting using Rich and Colorama
- **Progress Indicators**: Spinners and progress bars for long operations
- **Rich Panels**: Information displayed in beautiful bordered panels
- **ASCII Art Banner**: Professional-looking application banner
- **Status Messages**: Clear feedback for all operations
- **Error Handling**: Graceful error handling with helpful messages
- **Markdown Rendering**: Beautifully renders LLM responses with proper formatting

## 📝 Markdown Support

The agent now properly renders markdown output from the LLM, including:
- **Headers** (H1, H2, H3) with proper styling
- **Lists** (ordered and unordered)
- **Code blocks** with syntax highlighting
- **Bold and italic text**
- **Links** and other markdown elements
- **Fallback rendering** if markdown parsing fails

## ⚙️ Configuration

- **CV_PATH**: Path to your CV file (default: `cv.pdf` in current directory)
- **GOOGLE_API_KEY**: Your Google AI API key for the language model
- **FIRECRAWL_API_KEY**: Your Firecrawl API key for web crawling

## 🔧 Dependencies

The enhanced CLI uses several libraries for a professional experience:
- **Rich**: Beautiful terminal output with tables, panels, progress bars, and markdown rendering
- **Colorama**: Cross-platform color support
- **Typer**: Modern CLI framework with rich markup
- **Pyfiglet**: ASCII art text generation
- **Markdown**: Markdown parsing and rendering support

## 📝 Notes

- The CV is loaded into memory when the agent starts
- All CV searches are performed against this in-memory vector store
- The agent can be restarted to reload the CV if needed
- Use `quit`, `exit`, or `bye` to exit the agent
- Press `Ctrl+C` to interrupt operations
- The interface automatically handles errors gracefully
- LLM responses are beautifully rendered with markdown formatting

## 🎯 Professional Features

- **Environment Validation**: Checks all required API keys before starting
- **Graceful Error Handling**: Beautiful error messages and recovery options
- **Interactive Prompts**: Rich prompts for user input when needed
- **Status Monitoring**: Real-time status updates for all operations
- **Command History**: Built-in commands for easy navigation
- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **Markdown Rendering**: Professional markdown output rendering
