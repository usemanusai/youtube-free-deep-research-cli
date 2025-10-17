#!/bin/bash
# Setup script for n8n RAG integration
# This script helps you set up all required services for the n8n workflow

set -e

echo "=========================================="
echo "n8n RAG Integration Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Check if Node.js is installed (for n8n)
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠ Node.js is not installed (optional for n8n)${NC}"
    echo "You can use Docker to run n8n instead"
else
    echo -e "${GREEN}✓ Node.js is installed${NC}"
fi

echo ""
echo "=========================================="
echo "Step 1: Start Qdrant Vector Database"
echo "=========================================="
echo ""

# Check if Qdrant is already running
if docker ps | grep -q qdrant; then
    echo -e "${GREEN}✓ Qdrant is already running${NC}"
else
    echo "Starting Qdrant..."
    docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
    echo -e "${GREEN}✓ Qdrant started on http://localhost:6333${NC}"
fi

# Create collection
echo "Creating Qdrant collection..."
sleep 3  # Wait for Qdrant to be ready
curl -X PUT 'http://localhost:6333/collections/documents' \
  -H 'Content-Type: application/json' \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine"
    }
  }' 2>/dev/null || echo -e "${YELLOW}Collection may already exist${NC}"

echo -e "${GREEN}✓ Qdrant collection 'documents' ready${NC}"

echo ""
echo "=========================================="
echo "Step 2: Start PostgreSQL (for chat memory)"
echo "=========================================="
echo ""

# Check if PostgreSQL is already running
if docker ps | grep -q postgres-n8n; then
    echo -e "${GREEN}✓ PostgreSQL is already running${NC}"
else
    echo "Starting PostgreSQL..."
    docker run -d --name postgres-n8n \
      -e POSTGRES_PASSWORD=n8n_password \
      -e POSTGRES_DB=n8n_chat \
      -p 5432:5432 \
      postgres:15
    echo -e "${GREEN}✓ PostgreSQL started on localhost:5432${NC}"
fi

# Create chat memory table
echo "Creating chat memory table..."
sleep 3  # Wait for PostgreSQL to be ready
docker exec -i postgres-n8n psql -U postgres -d n8n_chat <<EOF 2>/dev/null || echo -e "${YELLOW}Table may already exist${NC}"
CREATE TABLE IF NOT EXISTS chat_memory (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

echo -e "${GREEN}✓ PostgreSQL chat memory table ready${NC}"

echo ""
echo "=========================================="
echo "Step 3: Install Ollama (Optional)"
echo "=========================================="
echo ""

if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is already installed${NC}"
    
    # Check if models are installed
    echo "Checking Ollama models..."
    if ollama list | grep -q llama3.1; then
        echo -e "${GREEN}✓ llama3.1 model is installed${NC}"
    else
        echo "Pulling llama3.1 model..."
        ollama pull llama3.1:latest
    fi
    
    if ollama list | grep -q nomic-embed-text; then
        echo -e "${GREEN}✓ nomic-embed-text model is installed${NC}"
    else
        echo "Pulling nomic-embed-text model..."
        ollama pull nomic-embed-text:latest
    fi
else
    echo -e "${YELLOW}⚠ Ollama is not installed${NC}"
    echo "Install Ollama from: https://ollama.ai/download"
    echo "Or use OpenRouter API instead (configure in .env)"
fi

echo ""
echo "=========================================="
echo "Step 4: Start n8n"
echo "=========================================="
echo ""

# Check if n8n is already running
if docker ps | grep -q n8n; then
    echo -e "${GREEN}✓ n8n is already running${NC}"
else
    echo "Starting n8n..."
    docker run -d --name n8n \
      -p 5678:5678 \
      -v ~/.n8n:/home/node/.n8n \
      n8nio/n8n
    echo -e "${GREEN}✓ n8n started on http://localhost:5678${NC}"
    echo ""
    echo -e "${YELLOW}Please wait 10 seconds for n8n to start...${NC}"
    sleep 10
fi

echo ""
echo "=========================================="
echo "Step 5: Configure .env file"
echo "=========================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    # Check if N8N_WEBHOOK_URL is configured
    if grep -q "^N8N_WEBHOOK_URL=" .env; then
        echo -e "${GREEN}✓ N8N_WEBHOOK_URL is already configured${NC}"
    else
        echo "Adding N8N_WEBHOOK_URL to .env..."
        echo "" >> .env
        echo "# n8n RAG Integration" >> .env
        echo "N8N_WEBHOOK_URL=http://localhost:5678/webhook/invoke_n8n_agent" >> .env
        echo -e "${GREEN}✓ N8N_WEBHOOK_URL added to .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env file..."
    cat > .env <<EOF
# n8n RAG Integration
N8N_WEBHOOK_URL=http://localhost:5678/webhook/invoke_n8n_agent

# OpenRouter API (optional - alternative to Ollama)
OPENROUTER_API_KEY=your_openrouter_api_key_here
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
fi

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}All services are running:${NC}"
echo "  • Qdrant Vector Database: http://localhost:6333"
echo "  • PostgreSQL: localhost:5432"
echo "  • n8n: http://localhost:5678"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Open n8n at http://localhost:5678"
echo ""
echo "2. Import the workflow:"
echo "   - Click 'Workflows' → 'Import from File'"
echo "   - Select: youtube_chat_cli_main/Local RAG AI Agent.json"
echo ""
echo "3. Configure n8n credentials:"
echo "   - Qdrant: http://localhost:6333 (no API key)"
echo "   - PostgreSQL: localhost:5432, db=n8n_chat, user=postgres, password=n8n_password"
echo "   - Ollama: http://localhost:11434 (if installed)"
echo "   - OpenRouter: Add your API key from .env"
echo ""
echo "4. Activate the workflow in n8n"
echo ""
echo "5. Test the integration:"
echo "   python -m youtube_chat_cli_main.cli invoke-n8n \"Hello, can you help me?\""
echo ""
echo "6. Process files:"
echo "   python -m youtube_chat_cli_main.cli process-file document.pdf"
echo ""
echo "7. Generate podcasts from RAG:"
echo "   python -m youtube_chat_cli_main.cli generate-podcast-from-rag \\"
echo "       --query \"Summarize the uploaded documents\""
echo ""
echo -e "${GREEN}For detailed instructions, see: N8N_INTEGRATION_ANALYSIS_AND_FIX.md${NC}"
echo ""

