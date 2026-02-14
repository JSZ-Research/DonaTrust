import numpy as np
import json
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# Initialize SocketIO with CORS allowed for local development
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = "gestures.json"
MATCH_THRESHOLD = 0.25

def load_templates():
    """Load saved gesture features from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return {k: np.array(v) for k, v in data.items()}
        except Exception as e:
            print(f"Error loading templates: {e}")
    return {}

# Global variable to store gesture templates
templates = load_templates()

def save_templates(t_dict):
    """Save current templates to JSON file."""
    try:
        serializable_data = {k: v.tolist() for k, v in t_dict.items()}
        with open(DATA_FILE, 'w') as f:
            json.dump(serializable_data, f)
    except Exception as e:
        print(f"Save failed: {e}")

@app.route('/')
def index():
    """Render the main UI."""
    return render_template('index.html')

@socketio.on('process_frame')
def handle_frame(data):
    """Compare incoming features with saved templates."""
    global templates
    if not data.get('features'):
        return

    features = np.array(data['features'])
    min_dist = float('inf')
    best_match = "Unknown"
    
    for name, temp in templates.items():
        dist = np.linalg.norm(features - temp)
        if dist < min_dist:
            min_dist = dist
            best_match = name
    
    # Return result only if distance is within threshold
    result = {
        "best_match": best_match if min_dist < MATCH_THRESHOLD else "Unknown",
        "dist": round(float(min_dist), 3)
    }
    emit('response_result', result)

@socketio.on('record_gesture')
def handle_record(data):
    """Save a new gesture template sent from the frontend."""
    global templates
    name = data['name']
    features = np.array(data['features'])
    templates[name] = features
    save_templates(templates)
    emit('record_status', {"status": "success", "name": name})

if __name__ == '__main__':
    # Run on port 5001 to avoid AirPlay conflict on macOS
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
