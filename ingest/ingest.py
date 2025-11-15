# ingest/ingest.py - USING VERIFIED IMPORTS
import os
from pathlib import Path

# Verified imports
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from .loaders import ResumeLoader
from app.deps import embeddings_manager, vectorstore_manager

class ResumeIngestor:
    def __init__(self):
        self.loader = ResumeLoader()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def ingest_documents(self) -> bool:
        """Main ingestion pipeline"""
        try:
            print("📚 Loading documents...")
            documents = self.loader.load_documents()
            
            if not documents:
                print("❌ No documents found in ./data/raw/")
                print("💡 Please add your resume (PDF/DOCX/TXT) to data/raw/ folder")
                return False
            
            print(f"✅ Loaded {len(documents)} documents")
            
            print("✂️  Splitting documents into chunks...")
            chunks = self.text_splitter.split_documents(documents)
            print(f"✅ Created {len(chunks)} chunks")
            
            print("🔮 Creating embeddings and vector store...")
            embeddings = embeddings_manager.get_embeddings()
            vectorstore = FAISS.from_documents(chunks, embeddings)
            
            print("💾 Saving vector store...")
            vectorstore_manager.save_vectorstore(vectorstore)
            
            print("🎉 Ingestion completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_existing_data(self) -> bool:
        """Check if vector store exists"""
        return os.path.exists(vectorstore_manager.vector_store_path)

if __name__ == "__main__":
    ingestor = ResumeIngestor()
    ingestor.ingest_documents()