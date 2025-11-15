FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/vectorstore

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run both services
CMD ["sh", "-c", "python app/api.py & streamlit run ui/streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]