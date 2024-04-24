import json
import os
import time
from flask import Flask, request, jsonify
import openai
from packaging import version

# Version check to ensure compatibility
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1")

# Set up Flask application
app = Flask(__name__)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
client = openai.Client(api_key=OPENAI_API_KEY)

# Load or create assistant ID
from functions import create_assistant  # Replace 'your_module' with the actual module name where 'create_assistant' is defined
assistant_id = create_assistant(client)

@app.route('/start', methods=['GET'])
def start_conversation():
    thread = client.Thread.create(assistant_id=assistant_id)
    return jsonify({"thread_id": thread.id})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')
    if not thread_id:
        return jsonify({"error": "Missing thread_id"}), 400

    message = client.Message.create(thread_id=thread_id, role="user", content={"type": "text", "text": user_input})
    run = client.Run.create(thread_id=thread_id, assistant_id=assistant_id)
    return jsonify({"run_id": run.id})

@app.route('/check', methods=['POST'])
def check_run_status():
    data = request.json
    thread_id = data.get('thread_id')
    run_id = data.get('run_id')
    if not thread_id or not run_id:
        return jsonify({"error": "Missing thread_id or run_id"}), 400

    start_time = time.time()
    while time.time() - start_time < 9:
        run_status = client.Run.retrieve(thread_id=thread_id, run_id=run_id)
        if run_status.status == 'completed':
            message_content = client.Message.list(thread_id=thread_id).data[0].content.text  # Assuming the text field exists
            return jsonify({"response": message_content, "status": "completed"})
        time.sleep(1)

    return jsonify({"response": "timeout"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
