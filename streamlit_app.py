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
from tools import TOOLS, initialize_vectorstore_with_cv
import tempfile
from ui_theme import DARK_THEME_CSS

# Page configuration
st.set_page_config(
    page_title="Draft 'n' Pray - AI Mail Writer",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
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

# Apply the dark mode CSS
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)


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
        if st.session_state.agent is None:
            checkpointer = InMemorySaver()
            llm = get_model()
            st.session_state.agent = create_react_agent(
                model=llm,
                tools=TOOLS,
                prompt=system_prompt,
                checkpointer=checkpointer,
            )
        return True
    except Exception as e:
        st.error(f"Failed to initialize AI Agent: {str(e)}")
        return False


def load_cv_from_upload(uploaded_file):
    """Load CV from uploaded file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Initialize vector store with the uploaded CV
        if initialize_vectorstore_with_cv(tmp_path):
            st.session_state.cv_loaded = True
            st.session_state.cv_path = uploaded_file.name
            # Clean up temporary file
            os.unlink(tmp_path)
            return True
        else:
            os.unlink(tmp_path)
            return False
    except Exception as e:
        st.error(f"Error loading CV: {str(e)}")
        return False


def main():
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

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        google_key = st.text_input(
            "Google API Key",
            type="password",
            help="Enter your Google API key for Gemini access",
            placeholder="Enter your key here...",
        )
        firecrawl_key = st.text_input(
            "Firecrawl API Key",
            type="password",
            help="Enter your Firecrawl API key for web crawling",
            placeholder="Enter your key here...",
        )

        # Set environment variables from user input
        if google_key:
            os.environ["GOOGLE_API_KEY"] = google_key
        if firecrawl_key:
            os.environ["FIRECRAWL_API_KEY"] = firecrawl_key

        st.markdown("### Controls")
        if st.button("🤖 Initialize Agent"):
            with st.spinner("Initializing AI Agent..."):
                initialize_agent()
        agent_status = "✅ Ready" if st.session_state.agent else "❌ Not initialized"
        st.caption(f"Agent: {agent_status}")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        show_tool_calls = st.toggle("Show tool calls", value=True)

        st.divider()
        st.markdown("### 📄 CV")
        uploaded_file = st.file_uploader(
            "Upload CV (PDF)", type=["pdf"], help="Personalize with your resume"
        )
        if uploaded_file is not None and st.button("💾 Load CV"):
            with st.spinner("Processing CV..."):
                if load_cv_from_upload(uploaded_file):
                    st.success("✅ CV loaded!")
                else:
                    st.error("❌ Failed to load CV")
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
        st.warning("⚠️ Initialize the AI Agent in the sidebar to get started!")
        return

    # Check if CV is loaded (only show warning if agent is ready)
    if st.session_state.agent and not st.session_state.cv_loaded:
        st.info("💡 Upload your CV in the sidebar for personalized emails")

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
                error_message = f"❌ Error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_message}
                )


if __name__ == "__main__":
    main()
