
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, Response
import subprocess
import os
import time
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Default credentials
USERNAME = 'admin'
PASSWORD = 'admin'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect_device():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    ip_address = request.json.get('ip_address')
    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400

    try:
        # Disconnect from all devices first
        subprocess.run(['adb', 'disconnect'], capture_output=True, text=True)
        
        # Connect to the new device
        result = subprocess.run(['adb', 'connect', ip_address], capture_output=True, text=True, timeout=10)
        if 'connected' in result.stdout or 'already connected' in result.stdout:
            session['device_ip'] = ip_address
            return jsonify({'success': True, 'message': f'Connected to {ip_address}'})
        else:
            return jsonify({'success': False, 'message': result.stderr or result.stdout})
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'Connection timed out.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/adb', methods=['POST'])
def adb_command():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    if not session.get('device_ip'):
        return jsonify({'error': 'No device connected'}), 400

    command = request.json.get('command')
    if not command:
        return jsonify({'error': 'Command is required'}), 400

    try:
        # Ensure the device is still connected
        ip = session['device_ip']
        connect_result = subprocess.run(['adb', 'connect', ip], capture_output=True, text=True)
        if 'connected' not in connect_result.stdout and 'already connected' not in connect_result.stdout:
            return jsonify({'error': 'Device disconnected. Please reconnect.'}), 400

        # Execute the command
        full_command = f'adb -s {ip} {command}'
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'output': result.stdout})
        else:
            return jsonify({'success': False, 'output': result.stderr or result.stdout})
    except Exception as e:
        return jsonify({'success': False, 'output': str(e)})

@app.route('/files')
def file_manager():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    path = request.args.get('path')

    if path == '/sdcard' or path == '/sdcard/':
        return redirect(url_for('file_manager'))

    if path is None:
        path = '/sdcard/'

    # Sanitize path
    if '..' in path:
        path = '/sdcard/'

    if not session.get('device_ip'):
        return render_template('file_manager.html', error='No device connected', path=path, items=[])

    try:
        ip = session['device_ip']
        # Ensure the device is still connected
        connect_result = subprocess.run(['adb', 'connect', ip], capture_output=True, text=True)
        if 'connected' not in connect_result.stdout and 'already connected' not in connect_result.stdout:
            return render_template('file_manager.html', error='Device disconnected. Please reconnect.', path=path, items=[])

        # Use ls -F to easily distinguish files and directories. Quote path to handle spaces.
        ls_command = f'adb -s {ip} shell ls -F "{path}"'
        result = subprocess.run(ls_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            return render_template('file_manager.html', error=result.stderr or result.stdout, path=path, items=[])

        items = []
        for name in result.stdout.strip().split('\n'):
            if not name:
                continue

            # adb ls can sometimes return weird stuff on error, filter it.
            if "No such file or directory" in name or "opendir failed" in name:
                continue
            
            if name.endswith('/'):
                file_type = 'directory'
                name = name[:-1]  # remove trailing slash
            elif name.endswith('*'):
                file_type = 'executable'
                name = name[:-1]
            elif name.endswith('@'):
                file_type = 'symlink'
                name = name[:-1]
            else:
                file_type = 'file'

            full_path = os.path.join(path, name)
            items.append({'name': name, 'type': file_type, 'path': full_path})

        return render_template('file_manager.html', items=items, path=path)
    except Exception as e:
        return render_template('file_manager.html', error=str(e), path=path, items=[])

@app.route('/view_file')
def view_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    path = request.args.get('path')
    if not path or not session.get('device_ip'):
        return 'File not found or no device connected.', 404

    try:
        ip = session['device_ip']
        # Pull the file from the device to a temporary location
        temp_file = f'/tmp/{os.path.basename(path)}'
        pull_command = f'adb -s {ip} pull "{path}" {temp_file}'
        result = subprocess.run(pull_command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            return f'Error pulling file: {result.stderr or result.stdout}', 500

        return send_file(temp_file, as_attachment=False)
    except Exception as e:
        return str(e), 500

@app.route('/delete_item', methods=['POST'])
def delete_item():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    path = request.form.get('path')
    if not path or not session.get('device_ip'):
        return 'File not found or no device connected.', 404

    try:
        ip = session['device_ip']
        # Command to delete a file or directory
        # Use rm -r for directories
        command = f'adb -s {ip} shell rm -r "{path}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            # Handle error, maybe flash a message
            pass

        # Redirect back to the file manager, to the parent directory of the deleted item
        parent_path = os.path.dirname(path)
        return redirect(url_for('file_manager', path=parent_path))
    except Exception as e:
        # Handle error
        return str(e), 500

@app.route('/screen_capture')
def screen_capture():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('screen_capture.html')

@app.route('/screenshot')
def screenshot():
    if not session.get('logged_in') or not session.get('device_ip'):
        return jsonify({'success': False, 'error': 'Not logged in or no device connected'})

    try:
        ip = session['device_ip']
        # Take screenshot
        screenshot_path = '/sdcard/screenshot.png'
        command = f'adb -s {ip} shell screencap -p {screenshot_path}'
        subprocess.run(command, shell=True, check=True)

        # Pull the screenshot
        local_path = f'static/screenshots/screenshot.png'
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        pull_command = f'adb -s {ip} pull {screenshot_path} {local_path}'
        subprocess.run(pull_command, shell=True, check=True)

        return jsonify({'success': True, 'file_path': '/' + local_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/screenrecord/<action>')
def screenrecord(action):
    if not session.get('logged_in') or not session.get('device_ip'):
        return jsonify({'success': False, 'error': 'Not logged in or no device connected'})

    ip = session['device_ip']
    video_path = '/sdcard/screenrecord.mp4'
    local_path = f'static/screenrecords/screenrecord.mp4'
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    if action == 'start':
        try:
            # Start screen recording in the background
            command = f'adb -s {ip} shell screenrecord {video_path}'
            process = subprocess.Popen(command, shell=True)
            session['screenrecord_pid'] = process.pid
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    elif action == 'stop':
        try:
            # Stop the screen recording process
            pid = session.get('screenrecord_pid')
            if pid:
                # Killing the adb process might not be enough, 
                # it is better to kill the shell process on the device.
                # This is a bit tricky, so for now we will just kill the adb process
                import signal
                os.kill(pid, signal.SIGTERM)
                session.pop('screenrecord_pid', None)

            # Pull the video
            pull_command = f'adb -s {ip} pull {video_path} {local_path}'
            subprocess.run(pull_command, shell=True, check=True)

            # Clean up the video on the device
            cleanup_command = f'adb -s {ip} shell rm {video_path}'
            subprocess.run(cleanup_command, shell=True)

            return jsonify({'success': True, 'file_path': '/' + local_path})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/live_screen')
def live_screen():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('live_screen.html')

@app.route('/live_screen_feed')
def live_screen_feed():
    if not session.get('logged_in') or not session.get('device_ip'):
        return Response(status=401)

    ip = session['device_ip']

    def generate(ip_address):
        while True:
            try:
                # Stream screenshot directly
                command = f'adb -s {ip_address} exec-out screencap -p'
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                img_bytes, stderr = process.communicate()

                if process.returncode != 0:
                    print(f"Error in live screen feed: {stderr.decode('utf-8')}")
                    break

                encoded_img = base64.b64encode(img_bytes).decode('utf-8')

                yield f"data:{encoded_img}\n\n"
                time.sleep(0.1) # Adjust for desired frame rate
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

    return Response(generate(ip), mimetype='text/event-stream')

@app.route('/app_management')
def app_management():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('app_management.html')

@app.route('/list_apps')
def list_apps():
    if not session.get('logged_in') or not session.get('device_ip'):
        return jsonify({'success': False, 'error': 'Not logged in or no device connected'})

    try:
        ip = session['device_ip']
        command = f'adb -s {ip} shell pm list packages -3' # -3 for third-party apps
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        apps = [line.split(':')[1] for line in result.stdout.strip().split('\n')]
        return jsonify({'success': True, 'apps': apps})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/shell_execute')
def shell_execute():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('shell_execute.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)







