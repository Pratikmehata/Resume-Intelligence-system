# ui/streamlit_app.py - UPDATED WITH FILE UPLOAD
import streamlit as st
import requests
import os
import tempfile
from pathlib import Path
import base64

# Configuration
API_BASE_URL = 'http://localhost:8000'

st.set_page_config(
    page_title='Resume Intelligence System',
    page_icon='💼',
    layout='wide'
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to data/raw directory"""
    try:
        # Create data/raw directory if it doesn't exist
        raw_dir = Path("data/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = raw_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path, True
    except Exception as e:
        return None, False

def process_uploaded_files():
    """Process uploaded files through the API"""
    try:
        response = requests.post(f"{API_BASE_URL}/ingest")
        if response.status_code == 200:
            return True, "Documents processed successfully!"
        else:
            return False, f"Processing failed: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    st.title('💼 Resume Intelligence System')
    st.markdown("### AI-Powered Career Assistant using RAG Architecture")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'files_uploaded' not in st.session_state:
        st.session_state.files_uploaded = False
    if 'processed' not in st.session_state:
        st.session_state.processed = False

    # Sidebar
    with st.sidebar:
        st.header('📁 Document Management')
        
        # File upload section
        st.subheader("Upload Resume")
        uploaded_files = st.file_uploader(
            "Choose resume files",
            type=['pdf', 'docx', 'txt', 'csv'],
            accept_multiple_files=True,
            help="Supported formats: PDF, DOCX, TXT, CSV"
        )
        
        # Upload and process buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if uploaded_files and st.button('📤 Upload Files'):
                success_count = 0
                for uploaded_file in uploaded_files:
                    file_path, success = save_uploaded_file(uploaded_file)
                    if success:
                        st.success(f"✅ {uploaded_file.name}")
                        success_count += 1
                    else:
                        st.error(f"❌ {uploaded_file.name}")
                
                if success_count > 0:
                    st.session_state.files_uploaded = True
                    st.session_state.processed = False
        
        with col2:
            if st.session_state.files_uploaded and st.button('🔄 Process Documents'):
                with st.spinner('Processing documents... This may take a few minutes.'):
                    success, message = process_uploaded_files()
                    if success:
                        st.success(message)
                        st.session_state.processed = True
                    else:
                        st.error(message)
        
        # Display uploaded files
        if st.session_state.files_uploaded:
            st.subheader("📋 Uploaded Files")
            raw_dir = Path("data/raw")
            if raw_dir.exists():
                files = list(raw_dir.glob("*"))
                for file in files:
                    st.write(f"• {file.name}")
        
        # System status
        st.subheader("🔧 System Status")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                st.success("✅ API Connected")
                st.info(f"RAG System: {'✅ Ready' if status_data.get('rag_available') else '❌ Not Ready'}")
            else:
                st.error("❌ API Not Available")
        except:
            st.error("❌ API Not Reachable")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button('🗑️ Clear All Files'):
            raw_dir = Path("data/raw")
            if raw_dir.exists():
                for file in raw_dir.glob("*"):
                    file.unlink()
                st.session_state.files_uploaded = False
                st.session_state.processed = False
                st.success("All files cleared!")
                st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with Your Resume")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                if message.get("sources"):
                    with st.expander("📚 View Sources"):
                        for source in message["sources"]:
                            st.write(f"**File:** {source.get('source', 'Unknown')}")
                            st.write(f"**Type:** {source.get('type', 'Unknown')}")
                            st.write(f"**Content:** {source.get('content', '')}")
                            st.divider()
        
        # Chat input (only if documents are processed)
        if st.session_state.processed:
            if prompt := st.chat_input("Ask about your resume, skills, or career advice..."):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Searching your resume..."):
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/query",
                                json={"question": prompt},
                                timeout=30
                            )
                            if response.status_code == 200:
                                result = response.json()
                                st.markdown(result['answer'])
                                
                                # Show sources
                                if result.get('sources'):
                                    with st.expander("📚 Sources"):
                                        for source in result['sources']:
                                            st.write(f"**File:** {source.get('source', 'Unknown')}")
                                            st.write(f"**Type:** {source.get('type', 'Unknown')}")
                                            st.write(f"**Content:** {source.get('content', '')}")
                                            st.divider()
                                
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": result['answer'],
                                    "sources": result.get('sources', [])
                                })
                            else:
                                st.error(f"API Error: {response.status_code}")
                        except requests.exceptions.Timeout:
                            st.error("Request timed out. Please try again.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            st.info("📝 Please upload and process your resume documents to start chatting.")
    
    with col2:
        st.header("🔍 Job Matching")
        
        if st.session_state.processed:
            job_desc = st.text_area(
                "Paste a job description to find matching skills:",
                height=200,
                placeholder="Paste job description here..."
            )
            
            if st.button("Find Matches") and job_desc:
                with st.spinner("Finding matches..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/similar-jobs",
                            json={"job_description": job_desc, "k": 3},
                            timeout=30
                        )
                        if response.status_code == 200:
                            matches = response.json().get('similar_jobs', [])
                            if matches and not matches[0].get('error'):
                                st.success(f"🎯 Found {len(matches)} matches!")
                                for i, match in enumerate(matches, 1):
                                    with st.expander(f"Match #{i}: {match.get('type', 'Resume')}"):
                                        st.write(match.get('content', ''))
                                        st.write(f"**Source:** {match.get('source', 'Unknown')}")
                            else:
                                st.warning("No strong matches found. Try a different job description.")
                        else:
                            st.error("Failed to find matches")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.info("📄 Process your resume first to use job matching.")

        # Quick tips
        st.header("💡 Tips")
        st.markdown("""
        **Sample Questions:**
        - What are my technical skills?
        - What experience do I have with Python?
        - What are my strongest qualifications?
        - How should I tailor my resume for data science roles?
        
        **Supported Formats:**
        - PDF documents
        - Word documents (.docx)
        - Text files (.txt)
        - CSV files (for job descriptions)
        """)

if __name__ == '__main__':
    main()