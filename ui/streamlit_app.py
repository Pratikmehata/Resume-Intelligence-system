# CLOUD COMPATIBLE VERSION
import streamlit as st
import requests
import os
from pathlib import Path
import tempfile

# Configuration - Use environment variable for API URL
API_BASE_URL = os.getenv('API_URL', 'http://localhost:8000')

st.set_page_config(
    page_title='Resume Intelligence System',
    page_icon='💼',
    layout='wide'
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary directory"""
    try:
        # Use temp directory for Streamlit Cloud
        temp_dir = Path(tempfile.gettempdir()) / "resume_uploads"
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path, True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None, False

def main():
    st.title('💼 Resume Intelligence System')
    st.markdown("### AI-Powered Career Assistant")
    
    # Check if API is available
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        api_available = response.status_code == 200
    except:
        api_available = False
    
    if not api_available:
        st.warning("""
        ⚠️ **Backend API Not Available**
        
        For full functionality, please run the backend API locally:
        ```bash
        python -m app.api
        ```
        
        You can still upload and view resumes, but AI features will be limited.
        """)
    
    # File upload section
    st.header("📁 Upload Your Resume")
    
    uploaded_files = st.file_uploader(
        "Choose resume files (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload your resume to get started"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path, success = save_uploaded_file(uploaded_file)
            if success:
                st.success(f"✅ {uploaded_file.name}")
                
                # Display basic file info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Size", f"{len(uploaded_file.getvalue()) / 1024:.1f} KB")
                with col2:
                    st.metric("File Type", uploaded_file.type)
                with col3:
                    st.metric("Status", "Uploaded")
    
    # Demo section if API not available
    if not api_available:
        st.header("🎯 Sample Career Insights")
        
        st.info("""
        **With the full system running, you could:**
        
        🔍 **Ask questions like:**
        - "What are my technical skills?"
        - "Which projects show leadership experience?"
        - "What are my strongest qualifications?"
        
        📊 **Get AI-powered insights:**
        - Skill gap analysis
        - Job matching scores
        - Career growth suggestions
        
        💼 **Upload resumes in:**
        - PDF, Word, Text formats
        - Multiple files for comparison
        """)
        
        # Sample interaction
        if st.button("🚀 See Demo Response"):
            st.success("""
            **Sample AI Response (with full system):**
            
            **Skills Found:** Python, Machine Learning, Data Analysis, Web Development
            **Strongest Projects:** 
            - AI Recommendation System (85% accuracy)
            - Customer Analytics Dashboard
            **Career Suggestions:** Focus on Data Science roles, enhance cloud skills
            """)
    
    # If API is available, show full features
    if api_available:
        st.header("💬 Chat with Your Resume")
        
        question = st.text_input("Ask about your skills, experience, or career advice:")
        
        if question and st.button("Get Insights"):
            try:
                with st.spinner("Analyzing your resume..."):
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={"question": question},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("🤖 AI Analysis Complete")
                        st.write(result.get('answer', 'No response received'))
                    else:
                        st.error("Failed to get response from AI system")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
