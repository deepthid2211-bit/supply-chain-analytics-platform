#!/bin/bash

# Supply Chain Analytics Chatbot - Setup Script
# This script sets up the chatbot environment

set -e  # Exit on error

echo "🚀 Setting up Supply Chain Analytics Chatbot..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Create .env from template if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - Snowflake account details"
    echo "   - OpenAI API key"
    echo "   - Groq API key (optional)"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Create data directory
mkdir -p data
echo "✓ Data directory created"

# Summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Run the chatbot:"
echo "   streamlit run app.py"
echo ""
echo "3. Open browser at: http://localhost:8501"
echo ""
echo "📚 Documentation:"
echo "   - README.md: Full feature documentation"
echo "   - DEPLOYMENT.md: Deploy to Streamlit Cloud"
echo ""
echo "Good luck! 🎉"
