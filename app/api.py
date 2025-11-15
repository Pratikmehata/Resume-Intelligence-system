from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ingest.ingest import ResumeIngestor
import uvicorn
import traceback

app = FastAPI(title='Resume RAG Assistant', version='1.0.0')

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Try to import RAG system
RAG_AVAILABLE = False
rag_system = None

try:
    from app.rag import rag_system
    RAG_AVAILABLE = True
    print('✅ RAG system loaded successfully')
except ImportError as e:
    print(f'❌ Failed to import RAG system: {e}')
    traceback.print_exc()

# Pydantic models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]

class SimilarJobsRequest(BaseModel):
    job_description: str
    k: Optional[int] = 3

class IngestionResponse(BaseModel):
    success: bool
    message: str

# Routes
@app.get('/')
async def root():
    return {'message': 'Resume RAG Assistant API', 'rag_available': RAG_AVAILABLE}

@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'rag_available': RAG_AVAILABLE}

@app.post('/query', response_model=QueryResponse)
async def query_resume(request: QueryRequest):
    if not RAG_AVAILABLE:
        return QueryResponse(
            answer='RAG system not available. Please check server logs.',
            sources=[]
        )
    
    try:
        print(f'🚀 Received query: {request.question}')
        result = rag_system.simple_search(request.question)
        print(f'✅ Query completed')
        return QueryResponse(**result)
    except Exception as e:
        print(f'❌ Query failed: {e}')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/similar-jobs')
async def find_similar_jobs(request: SimilarJobsRequest):
    if not RAG_AVAILABLE:
        return {'similar_jobs': [{'error': 'RAG system not available'}]}
    
    try:
        similar = rag_system.get_similar_jobs(request.job_description, request.k)
        return {'similar_jobs': similar}
    except Exception as e:
        print(f'❌ Similar jobs failed: {e}')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/ingest')
async def ingest_documents():
    try:
        ingestor = ResumeIngestor()
        success = ingestor.ingest_documents()
        
        if success:
            return IngestionResponse(success=True, message='Documents ingested successfully')
        else:
            return IngestionResponse(success=False, message='Failed to ingest documents')
    except Exception as e:
        print(f'❌ Ingestion failed: {e}')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/status')
async def system_status():
    ingestor = ResumeIngestor()
    return {
        'vector_store_exists': ingestor.check_existing_data(),
        'rag_available': RAG_AVAILABLE,
        'embeddings_type': 'Local HuggingFace'
    }

if __name__ == '__main__':
    print('Starting FastAPI server...')
    uvicorn.run(app, host='0.0.0.0', port=8000)
