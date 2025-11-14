from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Gemini client
# The client gets the API key from the environment variable `GEMINI_API_KEY`
gemini_api_key = os.getenv('GEMINI_API_KEY')
client = None
if gemini_api_key:
    try:
        # Can use genai.Client() if env var is set, or pass explicitly
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini client: {e}")
        client = None
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")

# File paths
AUTH_FILE = 'static/auth.json'
HISTORY_FILE = 'static/history.json'
HOSPITALS_FILE = 'static/hospitals.json'

# Ensure JSON files exist
def init_json_files():
    if not os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump({"health_score": 0, "records": []}, f)
    if not os.path.exists(HOSPITALS_FILE):
        with open(HOSPITALS_FILE, 'w') as f:
            json.dump([], f)

init_json_files()

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def get_user(username):
    users = load_json(AUTH_FILE)
    for user in users:
        if user['username'] == username:
            # Ensure health_score is integer when retrieving
            if 'health_score' in user:
                user['health_score'] = int(max(0, min(100, round(user['health_score']))))
            return user
    return None

def update_user(username, updates):
    users = load_json(AUTH_FILE)
    for i, user in enumerate(users):
        if user['username'] == username:
            users[i].update(updates)
            # Ensure health_score is always an integer
            if 'health_score' in users[i]:
                users[i]['health_score'] = int(max(0, min(100, round(users[i]['health_score']))))
            save_json(AUTH_FILE, users)
            return True
    return False

def get_history():
    return load_json(HISTORY_FILE)

def save_history(data):
    save_json(HISTORY_FILE, data)

def update_health_score(username, severity):
    user = get_user(username)
    if not user:
        return 0
    
    # Ensure health_score is an integer
    current_score = int(user.get('health_score', 0))
    
    if severity == 'normal':
        current_score = min(100, current_score + 15)
    elif severity == 'mild':
        current_score = max(0, current_score - 5)
    elif severity == 'serious':
        current_score = max(0, current_score - 15)
    
    # Ensure score is integer and within bounds
    current_score = int(min(100, max(0, current_score)))
    
    update_user(username, {'health_score': current_score})
    return current_score

@app.route('/')
def index():
    if 'username' in session:
        user = get_user(session['username'])
        if user and user.get('health_score', 0) == 0:
            return redirect(url_for('quiz'))
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        user = get_user(username)
        if user and user['password'] == password:
            session['username'] = username
            return jsonify({
                'success': True,
                'health_score': user.get('health_score', 0),
                'needs_quiz': user.get('health_score', 0) == 0
            })
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        if len(username) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 4:
            return jsonify({'success': False, 'message': 'Password must be at least 4 characters'}), 400
        
        users = load_json(AUTH_FILE)
        if any(u['username'] == username for u in users):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        new_user = {
            'username': username,
            'password': password,
            'health_score': 0,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        users.append(new_user)
        save_json(AUTH_FILE, users)
        
        session['username'] = username
        return jsonify({
            'success': True,
            'needs_quiz': True
        })
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.json
        answers = data.get('answers', [])
        
        if len(answers) != 10:
            return jsonify({'success': False, 'message': 'Please answer all questions'}), 400
        
        # Calculate score (each question worth 10 points)
        # Ensure all answers are valid numbers
        try:
            answers = [float(a) for a in answers]
            score = sum(answers)
            score = int(min(100, max(0, round(score))))
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'message': f'Invalid answer format: {str(e)}'}), 400
        
        # Update user health score
        username = session['username']
        update_user(username, {'health_score': score})
        
        # Save to history
        history = get_history()
        history['health_score'] = score
        save_history(history)
        
        return jsonify({
            'success': True,
            'score': score,
            'message': 'Quiz completed successfully'
        })
    
    return render_template('quiz.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['username'])
    health_score = int(user.get('health_score', 0))
    health_score = max(0, min(100, health_score))  # Ensure 0-100 range
    return render_template('chat.html', health_score=health_score)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    symptom = data.get('symptom', '').strip()
    
    if not symptom:
        return jsonify({'error': 'Symptom required'}), 400
    
    if not gemini_api_key or not client:
        return jsonify({'error': 'Gemini API not configured'}), 500
    
    # Gemini prompt
    system_prompt = """You are Arogya Gemini, a safe and concise health triage assistant.

Classify the user's condition:
🟢 Normal → minor lifestyle issues (fatigue, tired, dry throat, slight sneeze)
🟡 Mild → common cold, mild fever, cough, body pain
🔴 Serious → high fever, chest pain, breathing trouble, bleeding, chronic symptoms

Respond in 2–4 short sentences:
1. Start with severity emoji.
2. Give simple care suggestions.
3. If Serious → say: "Visit a doctor immediately. Tell me your city."
4. If Mild → say: "If persists for 2+ days, consider doctor."
5. If Normal → NO doctor or location mention.
Never diagnose diseases. Never repeat greetings."""
    
    try:
        # Create the content with system prompt and user symptom
        full_content = f"{system_prompt}\n\nUser symptom: {symptom}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_content
        )
        
        # Handle different response formats
        reply = None
        if hasattr(response, 'text'):
            reply = response.text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content'):
                if hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                    reply = candidate.content.parts[0].text
                elif hasattr(candidate.content, 'text'):
                    reply = candidate.content.text
        elif isinstance(response, str):
            reply = response
        
        if not reply:
            # Try to get any text from response
            reply = str(response)
            print(f"Warning: Unexpected response format: {type(response)}")
            print(f"Response attributes: {dir(response)}")
        
        reply = reply.strip() if reply else ""
        
        if not reply:
            return jsonify({'error': 'Empty response from AI. Check API key and model name.'}), 500
        
        # Determine severity
        severity = 'normal'
        if '🔴' in reply or 'Serious' in reply:
            severity = 'serious'
        elif '🟡' in reply or 'Mild' in reply:
            severity = 'mild'
        
        # Update health score
        username = session['username']
        new_score = update_health_score(username, severity)
        
        # Save to history
        history = get_history()
        record = {
            'username': username,
            'symptom': symptom,
            'reply': reply,
            'severity': severity,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        history['records'].append(record)
        # Keep only last 20 records per user (filter and keep last 20 for this user)
        user_records = [r for r in history['records'] if r.get('username') == username]
        if len(user_records) > 20:
            # Remove oldest records for this user
            user_records = user_records[-20:]
            # Update history: remove all user records and add back the last 20
            history['records'] = [r for r in history['records'] if r.get('username') != username] + user_records
        save_history(history)
        
        return jsonify({
            'reply': reply,
            'severity': severity,
            'health_score': new_score
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        print(traceback.format_exc())
        return jsonify({'error': f'AI error: {error_msg}. Please check if GEMINI_API_KEY is valid.'}), 500

@app.route('/hospitals')
def hospitals():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    hospitals_data = load_json(HOSPITALS_FILE)
    return render_template('hospitals.html', hospitals=hospitals_data)

@app.route('/api/hospitals/nearby', methods=['POST'])
def nearby_hospitals():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude required'}), 400
    
    try:
        import urllib.request
        import urllib.parse
        
        overpass_url = f"https://overpass-api.de/api/interpreter?data=[out:json];node[\"amenity\"=\"hospital\"](around:5000,{lat},{lon});out;"
        
        with urllib.request.urlopen(overpass_url) as response:
            data = json.loads(response.read().decode())
        
        hospitals = []
        for element in data.get('elements', []):
            tags = element.get('tags', {})
            hospitals.append({
                'name': tags.get('name', 'Unknown Hospital'),
                'address': tags.get('addr:full', tags.get('addr:street', 'Address not available')),
                'lat': element.get('lat'),
                'lon': element.get('lon')
            })
        
        return jsonify({'hospitals': hospitals})
    except Exception as e:
        return jsonify({'error': f'Error fetching hospitals: {str(e)}'}), 500

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    history_data = get_history()
    user = get_user(username)
    
    # Filter records for current user
    user_records = [r for r in history_data.get('records', []) if r.get('username') == username]
    
    health_score = int(user.get('health_score', 0))
    health_score = max(0, min(100, health_score))  # Ensure 0-100 range
    
    return render_template('history.html', 
                         history=user_records,
                         health_score=health_score)

@app.route('/api/health-score')
def get_health_score():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = get_user(session['username'])
    health_score = int(user.get('health_score', 0))
    health_score = max(0, min(100, health_score))  # Ensure 0-100 range
    return jsonify({'health_score': health_score})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

