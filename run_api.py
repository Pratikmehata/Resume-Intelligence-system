# run_api.py - This will fix Python path issues
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

print(f'Running from: {project_root}')
print(f'Python path: {sys.path[0]}')

try:
    from app.api import app
    import uvicorn
    
    print('✅ All imports successful! Starting server...')
    uvicorn.run(app, host='0.0.0.0', port=8000)
    
except Exception as e:
    print(f'❌ Failed to start: {e}')
    import traceback
    traceback.print_exc()
    input('Press Enter to exit...')
