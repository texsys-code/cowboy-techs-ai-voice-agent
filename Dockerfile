# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files - be explicit about what we copy
COPY agent.py .
COPY config.py .

# Copy lib directory contents (excluding __pycache__)
COPY lib/ ./lib/

# Copy instructions directory
COPY instructions/ ./instructions/

# Clean up any __pycache__ directories that might have been copied
RUN find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Verify the lib directory structure
RUN ls -la lib/ && ls -la lib/call_tools/

RUN python agent.py download-files

# Create .env file with environment variables
# These will be overridden by docker run -e or docker-compose
ENV LIVEKIT_API_KEY=""
ENV LIVEKIT_API_SECRET=""
ENV LIVEKIT_URL="ws://localhost:7881"
ENV DEEPGRAM_API_KEY=""
ENV OPENAI_API_KEY=""
ENV CARTESIA_API_KEY=""
ENV HALO_CLIENT_ID=""
ENV HALO_CLIENT_SECRET=""
ENV HALO_API_URL="https://intergrated.halopsa.com/api"
ENV TZ="America/Chicago"
ENV AGENT_NAME="telephony_agent"

# Expose port (if needed for any web interface)
EXPOSE 8080 7881 7882

# Set the default command
CMD ["python", "agent.py", "start"] 