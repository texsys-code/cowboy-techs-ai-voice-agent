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

# Copy application files
COPY telephony_agent.py .
COPY halo_api.py .
COPY config.py .

RUN python telephony_agent.py download-files

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
EXPOSE 8080

# Set the default command
CMD ["python", "telephony_agent.py", "start"] 