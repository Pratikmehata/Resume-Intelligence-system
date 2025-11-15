from app.deps import vectorstore_manager
from typing import List, Dict, Any
import traceback

class ResumeRAG:
    def __init__(self):
        try:
            self.vectorstore = vectorstore_manager.get_vectorstore()
            print('✅ Vector store loaded successfully')
        except Exception as e:
            print(f'❌ Could not load vector store: {e}')
            print('This is normal if you have not run ingestion yet')
            self.vectorstore = None
    
    def simple_search(self, question: str, k: int = 5) -> Dict[str, Any]:
        print(f'🔍 Searching for: {question}')
        
        if not self.vectorstore:
            error_msg = 'Vector store not available. Please run document ingestion first.'
            print(f'❌ {error_msg}')
            return {
                'answer': error_msg,
                'sources': []
            }
        
        try:
            print(f'📖 Performing similarity search with k={k}')
            docs = self.vectorstore.similarity_search(question, k=k)
            print(f'✅ Found {len(docs)} relevant documents')
            
            context = '\n\n'.join([doc.page_content for doc in docs])
            answer = f'I found these relevant sections from your resume:\n\n{context}'
            
            result = {
                'answer': answer,
                'sources': [
                    {
                        'source': doc.metadata.get('source', 'Unknown'),
                        'type': doc.metadata.get('type', 'Unknown'),
                        'content': doc.page_content[:200] + '...'
                    }
                    for doc in docs
                ]
            }
            
            print(f'✅ Search completed successfully')
            return result
            
        except Exception as e:
            error_msg = f'Error processing query: {e}'
            print(f'❌ {error_msg}')
            print('Full traceback:')
            traceback.print_exc()
            return {
                'answer': error_msg,
                'sources': []
            }
    
    def get_similar_jobs(self, job_description: str, k: int = 3) -> List[Dict]:
        if not self.vectorstore:
            return [{'error': 'Vector store not available'}]
        
        try:
            docs = self.vectorstore.similarity_search(job_description, k=k)
            return [
                {
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'Unknown'),
                    'type': doc.metadata.get('type', 'Unknown'),
                }
                for doc in docs
            ]
        except Exception as e:
            return [{'error': f'Failed to find similar jobs: {e}'}]

rag_system = ResumeRAG()
