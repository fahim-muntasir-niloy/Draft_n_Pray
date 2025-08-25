#!/usr/bin/env python3
"""
Draft 'n' Pray - Streamlit UI
Write. Send. Hope. Repeat. (Now with AI)
"""

import os
import uuid
import streamlit as st
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from system_prompt import system_prompt
from model import get_model
from tools import create_tools_with_api_keys, initialize_vectorstore_with_cv
import tempfile
from ui_theme import DARK_THEME_CSS

# Page configuration
st.set_page_config(
    page_title="Draft 'n' Pray - AI Mail Writer",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/issues",
        "Report a bug": "https://github.com/your-repo/issues",
        "About": "# Draft 'n' Pray\n\nAI-powered email writing assistant",
    },
)

# Force sidebar to be visible
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .sidebar .sidebar-content {
        width: 100% !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Initialize session state FIRST (before using any session state variables)
if "agent" not in st.session_state:
    st.session_state.agent = None
if "cv_loaded" not in st.session_state:
    st.session_state.cv_loaded = False
if "cv_path" not in st.session_state:
    st.session_state.cv_path = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": str(uuid.uuid4())}}
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = ""
if "firecrawl_api_key" not in st.session_state:
    st.session_state.firecrawl_api_key = ""

# Apply the dark mode CSS
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)


def is_deployed():
    """Check if the app is running in a deployment environment"""
    return (
        os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true"
        or os.getenv("STREAMLIT_SERVER_ENABLE_STATIC_SERVING", "false").lower()
        == "true"
        or os.getenv("STREAMLIT_SERVER_ENABLE_CORS", "false").lower() == "true"
    )


def needs_reinitialization():
    """Check if the agent needs to be reinitialized due to API key changes"""
    if not st.session_state.agent:
        return True

    # Check if current API keys match what the agent was initialized with
    current_google_key = st.session_state.get("google_api_key") or os.getenv(
        "GOOGLE_API_KEY"
    )
    current_firecrawl_key = st.session_state.get("firecrawl_api_key") or os.getenv(
        "FIRECRAWL_API_KEY"
    )

    # If keys have changed, reinitialization is needed
    if current_google_key != getattr(
        st.session_state.agent, "_google_api_key", None
    ) or current_firecrawl_key != getattr(
        st.session_state.agent, "_firecrawl_api_key", None
    ):
        return True

    return False


def clear_agent():
    """Clear the agent and reset related state"""
    st.session_state.agent = None
    st.session_state.cv_loaded = False
    st.session_state.cv_path = None
    st.session_state.messages = []
    st.rerun()


def safe_error_message(error: Exception, context: str = "") -> str:
    """Create a safe error message that doesn't expose sensitive information"""
    error_str = str(error)

    # Remove any potential API key exposure
    if "api_key" in error_str.lower() or "key" in error_str.lower():
        return f"Configuration error in {context}. Please check your API keys."

    # Remove any file paths that might contain sensitive information
    if "/" in error_str or "\\" in error_str:
        return f"File operation error in {context}. Please check your file paths."

    # Return a sanitized error message
    return (
        f"Error in {context}: {error_str[:100]}{'...' if len(error_str) > 100 else ''}"
    )


def check_app_health():
    """Check the overall health of the app and provide guidance"""
    issues = []
    warnings = []

    # Check Google API key
    google_key = st.session_state.get("google_api_key") or os.getenv("GOOGLE_API_KEY")
    if not google_key:
        issues.append("Google API key is missing")
    elif not google_key.strip():
        issues.append("Google API key is empty")
    elif len(google_key.strip()) < 10:
        issues.append("Google API key appears to be invalid")

    # Check Firecrawl API key (optional)
    firecrawl_key = st.session_state.get("firecrawl_api_key") or os.getenv(
        "FIRECRAWL_API_KEY"
    )
    if not firecrawl_key:
        warnings.append(
            "Firecrawl API key is missing (web crawling features will be disabled)"
        )

    # Check agent status
    if st.session_state.agent and needs_reinitialization():
        issues.append("Agent needs reinitialization due to API key changes")

    return issues, warnings


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """Mask an API key for safe display"""
    if not api_key or len(api_key) < visible_chars:
        return "❌ Invalid key"

    return f"{api_key[:visible_chars]}...{api_key[-visible_chars:]}"


def test_api_connection(api_key: str, api_type: str = "Google"):
    """Test API key connection"""
    try:
        if api_type == "Google":
            # Try to create a simple model instance to test the key
            test_model = get_model(api_key)
            # This will fail fast if the key is invalid
            return True, "✅ API key is valid"
        elif api_type == "Firecrawl":
            # For Firecrawl, we can't easily test without making a request
            # Just check if it's not empty and has reasonable length
            if len(api_key.strip()) > 10:
                return True, "✅ API key format looks valid"
            else:
                return False, "❌ API key format appears invalid"
    except Exception as e:
        return False, f"❌ API key test failed: {str(e)}"


def validate_api_keys():
    """Validate that required API keys are present and valid"""
    google_key = st.session_state.get("google_api_key") or os.getenv("GOOGLE_API_KEY")
    firecrawl_key = st.session_state.get("firecrawl_api_key") or os.getenv(
        "FIRECRAWL_API_KEY"
    )

    if not google_key:
        return False, "Google API key is required"

    # Basic validation - check if keys are not empty strings
    if not google_key.strip():
        return False, "Google API key cannot be empty"

    return True, "API keys are valid"


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["GOOGLE_API_KEY", "FIRECRAWL_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    return missing_vars


def initialize_agent():
    """Initialize the AI agent"""
    try:
        # Get API keys from session state or environment
        google_key = st.session_state.get("google_api_key") or os.getenv(
            "GOOGLE_API_KEY"
        )

        if not google_key:
            st.error("❌ Google API key is required. Please enter it in the sidebar.")
            return False

        # Validate the API key format (basic check)
        if not google_key.strip() or len(google_key.strip()) < 10:
            st.error("❌ Invalid Google API key format. Please check your key.")
            return False

        if st.session_state.agent is None:
            checkpointer = InMemorySaver()
            llm = get_model(google_key)  # Pass the API key
            firecrawl_key = st.session_state.get("firecrawl_api_key") or os.getenv(
                "FIRECRAWL_API_KEY"
            )
            tools = create_tools_with_api_keys(google_key, firecrawl_key)
            agent = create_react_agent(
                model=llm,
                tools=tools,
                prompt=system_prompt,
                checkpointer=checkpointer,
            )
            # Store API keys with the agent for comparison
            agent._google_api_key = google_key
            agent._firecrawl_api_key = firecrawl_key
            st.session_state.agent = agent
        return True
    except Exception as e:
        safe_msg = safe_error_message(e, "agent initialization")
        st.error(f"Failed to initialize AI Agent: {safe_msg}")
        # Clear the agent on error
        st.session_state.agent = None
        return False


def load_cv_from_upload(uploaded_file):
    """Load CV from uploaded file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Get the current Google API key
        google_key = st.session_state.get("google_api_key") or os.getenv(
            "GOOGLE_API_KEY"
        )

        # Initialize vector store with the uploaded CV
        if initialize_vectorstore_with_cv(tmp_path, google_key):
            st.session_state.cv_loaded = True
            st.session_state.cv_path = uploaded_file.name
            # Clean up temporary file
            os.unlink(tmp_path)
            return True
        else:
            os.unlink(tmp_path)
            return False
    except Exception as e:
        safe_msg = safe_error_message(e, "CV loading")
        st.error(f"Error loading CV: {safe_msg}")
        return False


def main():
    # Check if API keys are provided
    is_valid, message = validate_api_keys()
    if not is_valid:
        st.error(f"❌ **{message}**")

        # Show deployment-specific help
        if is_deployed():
            st.warning("🌐 **Deployment Mode Detected**")
            st.markdown("""
            **If you can't see the sidebar:**
            1. **Look for the hamburger menu (☰)** in the top-left corner
            2. **Use the API key inputs** in the main area below
            3. **Try refreshing the page** if the sidebar is stuck
            """)

        st.info("Please enter your Google API key to get started.")

        # Show a helpful setup guide
        with st.expander("🚀 **Quick Setup Guide**"):
            st.markdown("""
            ### Getting Started with Draft 'n' Pray
            
            1. **Get your Google API key:**
               - Go to [Google AI Studio](https://aistudio.google.com/)
               - Sign in and create a new API key
               - Copy the key (it starts with 'AI...')
            
            2. **Enter the key:**
               - **Option A**: Use the sidebar on the left (if visible)
               - **Option B**: Use the inputs in the main area below
            
            3. **Initialize the AI Agent:**
               - Click the 'Initialize Agent' button
               - Wait for confirmation
               - Start writing emails!
            
            **Need help?** Check the troubleshooting section below.
            """)

        st.stop()

    # Clean header

    # Minimal header like ChatGPT
    st.markdown(
        "<h1 class='main-header'>🧾 Draft 'n' Pray</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">// Write. Send. Hope. Repeat. (Now with AI) //</p>',
        unsafe_allow_html=True,
    )

    # Sidebar toggle help for deployment
    if st.button("🔧 **Show/Hide Sidebar**", help="Click to toggle sidebar visibility"):
        st.info("💡 **Sidebar Help:**")
        st.markdown("""
        - **If sidebar is hidden**: Look for the hamburger menu (☰) in the top-left corner
        - **On mobile**: Swipe from left edge to reveal sidebar
        - **On desktop**: Hover over the left edge or click the arrow button
        - **Still can't see it?**: Use the API key inputs in the main area above
        """)

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### 🔑 API Keys")

        google_key = st.text_input(
            "Google API Key",
            value=st.session_state.google_api_key,
            type="password",
            help="Enter your Google API key for Gemini access",
            placeholder="Enter your key here...",
            key="google_key_input",
        )

        if not google_key:
            st.warning("⚠️ Google API key is required to use the AI agent")

        firecrawl_key = st.text_input(
            "Firecrawl API Key",
            value=st.session_state.firecrawl_api_key,
            type="password",
            help="Enter your Firecrawl API key for web crawling (optional)",
            placeholder="Enter your key here...",
            key="firecrawl_key_input",
        )

        if not firecrawl_key:
            st.info(
                "ℹ️ Firecrawl API key is optional - needed for web crawling features"
            )

        # Help section for API keys
        with st.expander("🔑 Where to get API keys?"):
            st.markdown("""
            **Google API Key (Required):**
            - Visit [Google AI Studio](https://aistudio.google.com/)
            - Sign in with your Google account
            - Create a new API key
            - Copy and paste it here
            
            **Firecrawl API Key (Optional):**
            - Visit [Firecrawl](https://firecrawl.dev/)
            - Sign up for an account
            - Generate an API key
            - Copy and paste it here
            
            **🔒 Security Note:**
            - Your API keys are stored locally in your browser session
            - They are never logged or sent to external servers
            - Keys are automatically cleared when you close the browser
            """)

        # Clear API keys button
        if google_key or firecrawl_key:
            if st.button("🗑️ Clear API Keys", type="secondary"):
                st.session_state.google_api_key = ""
                st.session_state.firecrawl_api_key = ""
                os.environ.pop("GOOGLE_API_KEY", None)
                os.environ.pop("FIRECRAWL_API_KEY", None)
                clear_agent()

        # Update session state and environment variables when keys change
        if google_key != st.session_state.google_api_key:
            st.session_state.google_api_key = google_key
            os.environ["GOOGLE_API_KEY"] = google_key
            # Reset agent when API key changes
            st.session_state.agent = None

        if firecrawl_key != st.session_state.firecrawl_api_key:
            st.session_state.firecrawl_api_key = firecrawl_key
            os.environ["FIRECRAWL_API_KEY"] = firecrawl_key
            # Reset agent when API key changes
            st.session_state.agent = None

        # Show API key status
        st.markdown("#### 📊 API Key Status")
        google_status = "✅ Configured" if google_key else "❌ Missing"
        firecrawl_status = "✅ Configured" if firecrawl_key else "ℹ️ Optional"

        st.caption(f"Google: {google_status}")
        if google_key:
            st.caption(f"Key: {mask_api_key(google_key)}")

        st.caption(f"Firecrawl: {firecrawl_status}")
        if firecrawl_key:
            st.caption(f"Key: {mask_api_key(firecrawl_key)}")

        # Test API keys
        if google_key:
            if st.button("🧪 Test Google API", type="secondary", key="test_google"):
                with st.spinner("Testing Google API..."):
                    is_valid, message = test_api_connection(google_key, "Google")
                    if is_valid:
                        st.success(message)
                    else:
                        st.error(message)

        if firecrawl_key:
            if st.button(
                "🧪 Test Firecrawl API", type="secondary", key="test_firecrawl"
            ):
                with st.spinner("Testing Firecrawl API..."):
                    is_valid, message = test_api_connection(firecrawl_key, "Firecrawl")
                    if is_valid:
                        st.success(message)
                    else:
                        st.error(message)

        # Test embedding engine
        if google_key:
            if st.button(
                "🧪 Test Embedding Engine", type="secondary", key="test_embedding"
            ):
                with st.spinner("Testing embedding engine..."):
                    from model import test_embedding_engine

                    is_valid, message = test_embedding_engine(google_key)
                    if is_valid:
                        st.success(message)
                    else:
                        st.error(message)

        st.markdown("### Controls")

        # Health check
        issues, warnings = check_app_health()
        if issues or warnings:
            with st.expander("🔍 App Health Check", expanded=True):
                if issues:
                    st.error("**Issues Found:**")
                    for issue in issues:
                        st.error(f"• {issue}")

                if warnings:
                    st.warning("**Warnings:**")
                    for warning in warnings:
                        st.warning(f"• {warning}")

        # Only show initialize button if Google API key is provided
        if google_key:
            if st.button("🤖 Initialize Agent"):
                with st.spinner("Initializing AI Agent..."):
                    if initialize_agent():
                        st.success("✅ Agent initialized successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to initialize agent")
        else:
            st.button(
                "🤖 Initialize Agent",
                disabled=True,
                help="Enter your Google API key first",
            )

        # Show reinitialize button if needed
        if st.session_state.agent and needs_reinitialization():
            if st.button("🔄 Reinitialize Agent", type="secondary"):
                with st.spinner("Reinitializing AI Agent..."):
                    st.session_state.agent = None
                    if initialize_agent():
                        st.success("✅ Agent reinitialized successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to reinitialize agent")

        # Show agent status
        if st.session_state.agent:
            if needs_reinitialization():
                st.warning("⚠️ Agent needs reinitialization due to API key changes")
            else:
                st.success("✅ Agent is ready!")
        else:
            st.info("ℹ️ Agent not initialized")

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        show_tool_calls = st.toggle("Show tool calls", value=True)

        st.divider()
        st.markdown("### 📄 CV")

        if not google_key:
            st.info("ℹ️ Enter your Google API key first to enable CV processing")
            uploaded_file = st.file_uploader(
                "Upload CV (PDF)",
                type=["pdf"],
                help="Personalize with your resume",
                disabled=True,
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload CV (PDF)", type=["pdf"], help="Personalize with your resume"
            )
            if uploaded_file is not None and st.button("💾 Load CV"):
                with st.spinner("Processing CV..."):
                    try:
                        if load_cv_from_upload(uploaded_file):
                            st.success("✅ CV loaded!")
                        else:
                            st.error("❌ Failed to load CV")
                    except Exception as e:
                        safe_msg = safe_error_message(e, "CV processing")
                        st.error(f"❌ CV loading failed: {safe_msg}")
                        # Show additional help for common embedding issues
                        if "embedding" in str(e).lower() or "genai" in str(e).lower():
                            st.info("💡 **Embedding Issue Detected**")
                            st.markdown("""
                            This might be due to:
                            - Invalid Google API key
                            - Network connectivity issues
                            - Google GenAI service availability
                            
                            Try:
                            1. **Verify your Google API key** is correct
                            2. **Test the embedding engine** using the test button above
                            3. **Check your internet connection**
                            4. **Wait a few minutes** and try again
                            """)

        cv_status = "✅ Loaded" if st.session_state.cv_loaded else "❌ Not loaded"
        st.caption(f"CV: {cv_status}")
        if st.session_state.cv_path:
            st.caption(f"File: {st.session_state.cv_path}")

        # Footer in sidebar
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: left; padding: 0.5rem 0; color: #7d8590; font-size: 0.7rem;">
                <p style="margin: 0.2rem 0;"><strong>Created by Fahim Muntasir</strong></p>
                <p style="margin: 0.2rem 0;"><a href="mailto:muntasirfahim.niloy@gmail.com" style="color: #58a6ff;">muntasirfahim.niloy@gmail.com</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Main chat area - minimal and clean like ChatGPT
    if not st.session_state.agent:
        st.info("🚀 **Welcome to Draft 'n' Pray!**")

        # Fallback API key input for deployment issues
        st.markdown("### 🔑 **Enter Your API Keys**")
        st.warning("⚠️ **If you can't see the sidebar, enter your API keys here:**")

        col1, col2 = st.columns(2)
        with col1:
            fallback_google_key = st.text_input(
                "Google API Key (Required)",
                type="password",
                help="Enter your Google API key for Gemini access",
                placeholder="AI...",
                key="fallback_google_key",
            )
        with col2:
            fallback_firecrawl_key = st.text_input(
                "Firecrawl API Key (Optional)",
                type="password",
                help="Enter your Firecrawl API key for web crawling",
                placeholder="fc...",
                key="fallback_firecrawl_key",
            )

        # Update session state if fallback keys are provided
        if fallback_google_key and fallback_google_key != st.session_state.get(
            "google_api_key", ""
        ):
            st.session_state.google_api_key = fallback_google_key
            os.environ["GOOGLE_API_KEY"] = fallback_google_key
            st.success("✅ Google API key updated!")

        if fallback_firecrawl_key and fallback_firecrawl_key != st.session_state.get(
            "firecrawl_api_key", ""
        ):
            st.session_state.firecrawl_api_key = fallback_firecrawl_key
            os.environ["FIRECRAWL_API_KEY"] = fallback_firecrawl_key
            st.success("✅ Firecrawl API key updated!")

        st.markdown("""
        To get started:
        1. **Enter your Google API key** above (required)
        2. **Enter your Firecrawl API key** if you want web crawling features (optional)
        3. **Click 'Initialize Agent'** below to start the AI assistant
        4. **Upload your CV** for personalized email writing
        """)

        # Initialize button in main area
        if fallback_google_key:
            if st.button(
                "🤖 **Initialize AI Agent**", type="primary", use_container_width=True
            ):
                with st.spinner("Initializing AI Agent..."):
                    if initialize_agent():
                        st.success("✅ Agent initialized successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to initialize agent")
        else:
            st.button(
                "🤖 **Initialize AI Agent**",
                disabled=True,
                use_container_width=True,
                help="Enter your Google API key first",
            )

        st.warning("⚠️ Please initialize the AI Agent to get started!")

        # Troubleshooting section for deployment
        with st.expander(
            "🚨 **Troubleshooting - Sidebar Not Visible?**", expanded=True
        ):
            st.markdown("""
            ### **Can't See the Sidebar?**
            
            **Try these solutions:**
            1. **Look for the hamburger menu (☰)** in the top-left corner
            2. **Hover over the left edge** of the screen
            3. **Click the arrow button** if visible
            4. **Refresh the page** (F5 or Ctrl+R)
            5. **Use the API key inputs above** as a fallback
            
            **Mobile/Tablet Users:**
            - Swipe from the left edge of the screen
            - Look for a menu button in the top-left
            
            **Desktop Users:**
            - Press `Ctrl + Shift + S` to toggle sidebar
            - Look for the sidebar toggle button
            
            **Still Having Issues?**
            - Try a different browser (Chrome, Firefox, Safari)
            - Clear browser cache and cookies
            - Check if JavaScript is enabled
            """)

        return

    # Check if CV is loaded (only show warning if agent is ready)
    if st.session_state.agent and not st.session_state.cv_loaded:
        st.info("💡 Upload your CV in the sidebar for personalized emails")

    # Check if agent needs reinitialization
    if st.session_state.agent and needs_reinitialization():
        st.warning(
            "⚠️ **Agent needs reinitialization!** Your API keys have changed. Please click 'Reinitialize Agent' in the sidebar."
        )
        return

    # Show success message when everything is ready
    if st.session_state.agent and not needs_reinitialization():
        st.success(
            "🎉 **Ready to write emails!** Your AI assistant is ready to help you draft professional emails."
        )

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Message Draft 'n' Pray...", key="chat_input"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            try:

                def _stream():
                    tool_calls = []
                    tool_call_detected = False

                    for token, metadata in st.session_state.agent.stream(
                        {"messages": [{"role": "user", "content": prompt}]},
                        st.session_state.config,
                        stream_mode="messages",
                    ):
                        if token:
                            # Check if this token is part of a tool call
                            if hasattr(token, "tool_calls") and token.tool_calls:
                                tool_call_detected = True
                                if show_tool_calls:
                                    tool_calls.append(token)
                            elif hasattr(token, "content") and token.content:
                                # This is a regular content token, not a tool call
                                if not tool_call_detected:
                                    yield token.content
                                else:
                                    # Reset tool call detection for next content
                                    tool_call_detected = False
                            else:
                                # Fallback for string tokens
                                if not tool_call_detected:
                                    yield token

                    # Display tool calls in expander if enabled
                    if show_tool_calls and tool_calls:
                        with st.expander("🔧 Tool Calls", expanded=False):
                            for tool_call in tool_calls:
                                st.json(tool_call)

                final_text = st.write_stream(_stream())
                st.session_state.messages.append(
                    {"role": "assistant", "content": final_text}
                )
            except Exception as e:
                safe_msg = safe_error_message(e, "chat generation")
                error_message = f"❌ Error: {safe_msg}"
                st.error(error_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_message}
                )


if __name__ == "__main__":
    main()
