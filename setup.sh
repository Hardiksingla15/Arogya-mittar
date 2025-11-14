#!/bin/bash

echo "Setting up Arogya Gemini..."
echo ""

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Creating .env file..."
if [ ! -f .env ]; then
    echo "GEMINI_API_KEY=AIzaSyDscXCAL4ffkc16CEoG0BaL6MuUc7XO9AE" > .env
    echo ".env file created!"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the application, use: python server.py"
echo "Then open http://localhost:5000 in your browser"

