import streamlit as st
import requests

# --- Configuration ---
API_URL = "https://ukgc-lccp-rag-api-bpkp.onrender.com/chat"
PAGE_TITLE = "UKGC LCCP Assistant"
PAGE_ICON = "⚖️"

# --- Page Setup ---
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="centered")

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.caption("Ask questions about the UK Gambling Commission LCCP (Licence Conditions and Codes of Practice).")

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Function to Format Sources ---
def format_sources(sources):
    """
    Generates a markdown representation of sources within an expander.
    """
    if not sources:
        return
    
    with st.expander("📚 View Sources & References", expanded=False):
        for idx, source in enumerate(sources):
            condition = source.get("condition", "Unknown Condition")
            context = source.get("context", "No context provided")
            links = source.get("links", [])
            
            st.markdown(f"**{idx + 1}. {condition}**")
            st.markdown(f"*Context: {context}*")
            
            if links:
                links_md = " | ".join([f"[Link {i+1}]({link})" for i, link in enumerate(links)])
                st.markdown(f"🔗 {links_md}")
            
            st.divider()

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the message has associated sources, display them
        if "sources" in message:
            format_sources(message["sources"])

# --- User Input Handling ---
if prompt := st.chat_input("Ex: What are the financial vulnerability check requirements?"):
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Fetch Response from API
    with st.chat_message("assistant"):
        with st.spinner("Analyzing LCCP documents..."):
            try:
                payload = {"question": prompt}
                headers = {
                    "accept": "application/json",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(API_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    answer_text = data.get("answer", "No answer provided.")
                    source_data = data.get("sources", [])
                    
                    # Display Answer
                    st.markdown(answer_text)
                    
                    # Display Sources (The "Grounding")
                    format_sources(source_data)
                    
                    # Save to History
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer_text,
                        "sources": source_data
                    })
                    
                else:
                    error_msg = f"Error {response.status_code}: Unable to fetch response."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.exceptions.ConnectionError:
                error_msg = "Failed to connect to the API. Please check if the server is running."
                st.error(error_msg)
            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}"
                st.error(error_msg)

# --- Sidebar Info ---
with st.sidebar:
    st.header("About")
    st.markdown("""
    This interface retrieves information using RAG (Retrieval-Augmented Generation) 
    over the UKGC LCCP documentation.
    
    **Features:**
    - Source Grounding
    - Direct Reference Links
    - Contextual Awareness
    """)
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()