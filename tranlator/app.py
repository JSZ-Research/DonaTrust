import numpy as np
import json
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = "gestures.json"
# Adjusted threshold for normalized Euclidean distance
MATCH_THRESHOLD = 0.4 

def load_templates():
    """Load hand feature templates from JSON."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Ensure every template is a flat numpy array
                return {k: np.array(v).flatten() for k, v in data.items()}
        except Exception as e:
            print(f"Error loading templates: {e}")
    return {}

templates = load_templates()

def save_templates(t_dict):
    """Save templates to local JSON file."""
    try:
        serializable_data = {k: v.tolist() for k, v in t_dict.items()}
        with open(DATA_FILE, 'w') as f:
            json.dump(serializable_data, f)
    except Exception as e:
        print(f"Save failed: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('process_frame')
def handle_frame(data):
    global templates
    features_list = data.get('features')
    
    if not features_list or len(features_list) != 42:
        return

    # Convert incoming list to numpy array
    input_vec = np.array(features_list)
    
    min_dist = float('inf')
    best_match = "Unknown"
    
    for name, temp in templates.items():
        if temp.shape != input_vec.shape:
            continue
            
        # Standard Euclidean distance
        dist = np.linalg.norm(input_vec - temp)
        if dist < min_dist:
            min_dist = dist
            best_match = name
    
    # Send result back to frontend
    emit('response_result', {
        "best_match": best_match if min_dist < MATCH_THRESHOLD else "Unknown",
        "dist": round(float(min_dist), 4)
    })

@socketio.on('record_gesture')
def handle_record(data):
    global templates
    name = data['name']
    features = np.array(data['features']).flatten()
    templates[name] = features
    save_templates(templates)
    emit('record_status', {"status": "success", "name": name})

if __name__ == '__main__':
    # Using port 5001 to avoid macOS AirPlay conflicts
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
