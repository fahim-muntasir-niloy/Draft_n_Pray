# 🧾 Draft 'n' Pray - AI Mail Writer

> **Write. Send. Hope. Repeat.** *(Now with AI)*

A powerful AI-powered email writing assistant that helps you craft personalized emails using your CV and web research. Available as both a **CLI tool** and **Streamlit web interface**.

![Streamlit UI Banner](images/streamlit_banner.png)

## ✨ Features

- 🤖 **AI-Powered Email Generation** - Advanced LLMs craft personalized emails
- 📄 **CV Integration** - Upload your CV for experience-based personalization
- 🌐 **Web Research** - Crawl websites to gather company/lab information
- 🧠 **Smart Tool Selection** - Automatically chooses the right tools for your request
- ⚡ **Real-time Streaming** - Live token streaming for better user experience
- 🎨 **Clean Interface** - Minimal, ChatGPT-like UI focused on content
- 🔑 **Smart API Management** - Interactive setup and secure storage of API keys

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Google API key for Gemini AI
- Firecrawl API key for web crawling

### Installation
```bash
# Clone the repository
git clone 
cd directory

# Install dependencies
pip install -r requirements.txt
```

## 🛠️ Usage Options

### Option 1: CLI Tool (Recommended for Developers)

**Interactive Setup:**
```bash
# Setup API keys interactively
python agent.py setup-keys

# Run the application
python agent.py
```

**Manual Setup:**
```bash
# Set environment variables
export GOOGLE_API_KEY="your_google_api_key"
export FIRECRAWL_API_KEY="your_firecrawl_api_key"

# Run the application
python agent.py
```

**Available CLI Commands:**
- `python agent.py` - Start the main application
- `python agent.py setup-keys` - Interactive API key setup
- `python agent.py check-keys` - Check current API key status
- `python agent.py --help` - Show all available commands

### Option 2: Streamlit Web UI

Perfect for non-technical users and deployment scenarios.

```bash
# Run the Streamlit app
streamlit run streamlit_app.py
```

Then open your browser and enter your API keys in the sidebar.

## 🔑 API Key Setup

### Required Keys

1. **Google API Key** - For Gemini LLM access
   - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
   
2. **Firecrawl API Key** - For web crawling capabilities
   - Get it from [Firecrawl](https://firecrawl.dev/)

### Setup Methods

**Method 1: Interactive Setup (Recommended)**
```bash
python agent.py setup-keys
```
This will:
- Prompt for missing API keys
- Store them securely in memory
- Offer to save to `.env` file
- Validate all keys before proceeding

**Method 2: Environment Variables**
```bash
export GOOGLE_API_KEY="your_key_here"
export FIRECRAWL_API_KEY="your_key_here"
```

**Method 3: .env File**
Create a `.env` file in your project directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
CV_PATH=cv.pdf  # Optional
```

## 📁 Project Structure

```
mail_writer_agent/
├── agent.py              # Enhanced CLI tool with API key management
├── streamlit_app.py      # Streamlit web interface
├── tools.py              # Tool definitions (CV search, web crawling)
├── model.py              # LLM model configuration
├── system_prompt.py      # Agent system prompt
├── ui_theme.py           # Streamlit UI theme
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (auto-created)
└── images/               # Banner images and assets
    └── streamlit_banner.png
```

## 💡 Example Prompts

### Email Generation
- "Crawl https://prof-site.edu and write an email to the professor about joining their lab"
- "Research this company and draft a cover letter for the software engineer position"

### CV Analysis
- "What are my programming languages?"
- "Summarize my work experience"
- "What technical skills do I have?"

### Research Tasks
- "Find the latest publications from this research group"
- "What are the main research areas of this lab?"

## 🔧 CLI Commands Reference

### Main Application
```bash
python agent.py                    # Start the main application
```

### API Key Management
```bash
python agent.py setup-keys         # Interactive API key setup
python agent.py check-keys         # Check current API key status
```

### Help and Information
```bash
python agent.py --help             # Show CLI help
python agent.py version            # Show version information
```

### In-App Commands (during chat)
- `help` - Show available commands
- `tools` - Show available tools
- `cv` - Show CV status
- `apikeys` - Show API key status
- `quit`, `exit`, `bye` - Exit the application

## 🌐 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect your repo to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy automatically
4. Users input their own API keys in the web interface

### Other Platforms
- **Heroku**: Use the Streamlit buildpack
- **Railway**: Deploy with Railway's Python support
- **Vercel**: Use Vercel's Python runtime

## 🔒 Security Notes

- API keys are stored securely in memory during the session
- The `.env` file is automatically created but should be kept secure
- **Never commit your `.env` file to version control**
- Use environment variables in production deployments

## 🎯 Use Cases

### Academic Applications
- Research lab applications
- Conference paper submissions
- Collaboration requests
- Grant applications

### Job Applications
- Cover letters
- Networking emails
- Follow-up messages
- Thank you notes

### Business Communication
- may be (wont recommend lol)

## 🔧 Customization

- **System Prompt**: Modify `system_prompt.py` to change agent behavior
- **Tools**: Add new tools in `tools.py`
- **UI Theme**: Customize the interface in `ui_theme.py`
- **Model**: Change LLM provider in `model.py`

## 🐛 Troubleshooting

### Common Issues

**API Key Errors:**
- Ensure both `GOOGLE_API_KEY` and `FIRECRAWL_API_KEY` are set
- Use `python agent.py check-keys` to verify status
- Run `python agent.py setup-keys` for interactive setup

**CV Loading Issues:**
- Check if CV file exists at the specified path
- Ensure CV is in PDF format
- Verify Google API key is valid for embeddings

**Web Crawling Issues:**
- Verify Firecrawl API key is valid
- Check if the target website is accessible
- Ensure URL format is correct

## 📚 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Creator

**Fahim Muntasir**  
📧 muntasirfahim.niloy@gmail.com

---

*Your supervisor won't answer, but at least your grammar's perfect.* 🎯
