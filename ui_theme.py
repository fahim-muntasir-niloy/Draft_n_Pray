"""
Reusable UI theme for the Streamlit app.
Contains a main dark mode without any sidebar hacks.
"""

# Minimal dark mode CSS with coding font - ChatGPT-like
DARK_THEME_CSS = """
<style>

    /* Global styling with system sans-serif fonts */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", "Helvetica Neue", Arial, sans-serif;
    }
    /* Let most elements inherit; avoid broad overrides that can break icon fonts */

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 820px;
        margin-left: auto;
        margin-right: auto;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Minimal header */
    .main-header {
        text-align: center;
        color: #58a6ff;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-family: inherit;
    }

    .subtitle {
        text-align: center;
        color: #984af7;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        opacity: 0.8;
    }

    /* Hide some Streamlit default elements (keep header for sidebar toggle) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar (non-fixed) */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }

    /* Chat messages */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
        margin-bottom: 1rem !important;
    }

    /* User message styling */
    .stChatMessage[data-testid="user-message"] > div {
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        background-color: #0f141a !important;
        padding: 0.75rem 1rem !important;
    }

    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] > div {
        border: 1px solid #30363d !important;
        border-left: 3px solid #238636 !important;
        border-radius: 12px !important;
        background-color: #0d1117 !important;
        padding: 0.75rem 1rem !important;
    }

    /* Chat input */
    .stChatInputContainer {
        border-top: 1px solid #30363d;
        background-color: #0d1117;
        padding: 1rem 0;
    }

    .stChatInput > div {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 9999px !important;
        padding: 0.6rem 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }

    .stChatInput input {
        background-color: transparent !important;
        color: #e6edf3 !important;
        font-family: inherit !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
        border: none !important;
    }

    .stChatInput input::placeholder {
        color: #7d8590 !important;
        font-family: inherit !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #21262d;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-family: inherit;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #30363d;
        border-color: #58a6ff;
    }

    /* File uploader */
    .stFileUploader {
        background-color: #161b22;
        border: 1px dashed #30363d;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Text elements */
    h1, h2, h3, h4, h5, h6 {
        color: #e6edf3 !important;
    }

    /* Avoid overriding generic spans/divs to preserve icon fonts */

    /* Status indicators */
    .status-success { color: #238636; font-weight: 600; }
    .status-error { color: #da3633; font-weight: 600; }
    .status-warning { color: #fb8500; font-weight: 600; }

    /* Ensure Material Symbols render correctly (for header/sidebar toggles) */
    .material-symbols-outlined,
    .material-symbols-rounded,
    .material-symbols-sharp {
        font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Symbols Sharp' !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* Sidebar toggle: use default Streamlit icon/behavior (no overrides) */

    /* Expander */
    .stExpander {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #58a6ff !important; }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 8px; background-color: #0d1117; }
    ::-webkit-scrollbar-thumb { background-color: #30363d; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background-color: #484f58; }

    /* Markdown and code */
    .stMarkdown { font-family: inherit !important; }
    code {
        background-color: #161b22 !important;
        color: #79c0ff !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: inherit !important;
    }
    pre {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        font-family: inherit !important;
    }
</style>
"""
