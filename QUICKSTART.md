# Quick Start Guide - Arogya Gemini

## 🚀 Fast Setup (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create .env File
Create a file named `.env` in the root directory with:
```
GEMINI_API_KEY=AIzaSyDscXCAL4ffkc16CEoG0BaL6MuUc7XO9AE
```

**OR** run the setup script:
- Windows: `setup.bat`
- Linux/Mac: `chmod +x setup.sh && ./setup.sh`

### Step 3: Run the Server
```bash
python server.py
```

Then open: **http://localhost:5000**

## 🔑 Default Login
- Username: `hardik`
- Password: `1234`

## ✅ Verify Everything Works

1. **Login** → Should redirect to quiz if health_score = 0
2. **Complete Quiz** → Should calculate score and redirect to chat
3. **Chat** → Type symptoms, test voice input (microphone button)
4. **Hospitals** → Search and use "Find Hospitals Near Me"
5. **History** → View your health records

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'genai'"
```bash
pip install google-genai
```

### "GEMINI_API_KEY not found"
- Make sure `.env` file exists in root directory
- Check that the file contains: `GEMINI_API_KEY=your_key_here`

### Server won't start
- Check if port 5000 is already in use
- Try: `python server.py` (should show "Running on http://127.0.0.1:5000")

### Voice input not working
- Use Chrome or Edge browser (best support)
- Allow microphone permissions when prompted

## 📁 Project Structure
```
arogya-mittar/
├── server.py          # Main Flask app
├── .env              # API keys (create this!)
├── requirements.txt  # Dependencies
├── templates/        # HTML pages
└── static/          # CSS, JS, JSON data
```

## 🎨 Features Ready
✅ User authentication (signup/login)
✅ Health quiz (10 questions)
✅ AI chat with Gemini 2.5 Flash
✅ Voice input/output
✅ Hospital search + map
✅ Health history
✅ Health score gauge (always visible)

Everything is ready to go! 🎉

