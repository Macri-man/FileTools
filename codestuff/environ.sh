#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")"

# Path to the virtual environment (adjust as needed)
VENV_PATH="$HOME/venv"

# Step 1: Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "🔧 Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH" || { echo "❌ Failed to create virtual environment"; exit 1; }
fi

# Step 2: Activate the virtual environment
echo "⚡ Activating virtual environment..."
source "$VENV_PATH/bin/activate" || { echo "❌ Failed to activate virtual environment"; exit 1; }

# Step 3: Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 4: Install required packages
if [ -f "requirements.txt" ]; then
    echo "📦 Installing packages from requirements.txt..."
    pip install -r requirements.txt || { echo "❌ Failed to install requirements"; exit 1; }
else
    echo "⚠️ requirements.txt not found!"
fi

# Step 5: Run your Streamlit app
echo "🚀 Starting app.py using Streamlit..."
streamlit run app.py
