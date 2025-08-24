# Draft 'n' Pray

![Draft 'n' Pray Banner](images/banner.png)

> **Write. Send. Hope. Repeat. (Now with AI)**

A powerful AI-powered CLI application that helps you draft professional emails and cover letters using your CV/resume as context. Built with LangChain, LangGraph, and Google's Generative AI.

## ✨ Features

- 🤖 **AI-Powered Writing**: Generate professional emails and cover letters using Google's Generative AI
- 📄 **CV Context**: Upload your CV/resume to provide relevant context for personalized content
- 🌐 **Web Research**: Integrate real-time web research using Firecrawl API
- 🎨 **Beautiful CLI**: Rich, colorful terminal interface with progress bars and panels
- 📚 **Knowledge Base**: Intelligent search through your CV content using vector embeddings
- 🔄 **Interactive Workflow**: Step-by-step guided process for creating professional communications

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- Google API Key for Generative AI
- Firecrawl API Key for web research

### Setup

1. **Clone the repository**
   ```bash
   git clone <Draft_n_Pray>
   cd Draft_n_pray
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   CV_PATH="PATH\TO\YOUR\CV.PDF"
   ```

4. **Get API Keys**
   - **Google API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your API key [basic usage is free!]
   - **Firecrawl API Key**: Visit [Firecrawl](https://firecrawl.dev/) to get your API key [you get free credits!]

## 🎯 Usage

```bash
$ python run.py
```


## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Generative AI API key | Yes |
| `FIRECRAWL_API_KEY` | Firecrawl API key for web research | Yes |

### Supported File Formats

- **CV/Resume**: PDF files
- **Output**: Markdown format (easily convertible to other formats)



## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Fahim Muntasir**
- Email: muntasirfahim.niloy@gmail.com
- GitHub: [@fahim-muntasir-niloy](https://github.com/fahim-muntasir-niloy)

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Google Generative AI](https://ai.google.dev/)
- Web research powered by [Firecrawl](https://firecrawl.dev/)
- Beautiful CLI thanks to [Rich](https://rich.readthedocs.io/)

---

**Draft 'n' Pray** 

Your supervisor won’t answer, but at least your grammar’s perfect. ✨
