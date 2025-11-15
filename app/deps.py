import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

class EmbeddingsManager:
    def __init__(self):
        self._embeddings = None
    
    def get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name='sentence-transformers/all-MiniLM-L6-v2',
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return self._embeddings

class VectorStoreManager:
    def __init__(self):
        self.embeddings_manager = EmbeddingsManager()
        self.vector_store_path = os.getenv('VECTOR_STORE_PATH', './data/vectorstore')
    
    def get_vectorstore(self):
        try:
            return FAISS.load_local(
                self.vector_store_path,
                self.embeddings_manager.get_embeddings(),
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            raise Exception(f'Failed to load vector store: {e}')
    
    def save_vectorstore(self, vectorstore):
        os.makedirs(self.vector_store_path, exist_ok=True)
        vectorstore.save_local(self.vector_store_path)

embeddings_manager = EmbeddingsManager()
vectorstore_manager = VectorStoreManager()
