from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # للجلسات

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

# كلمة المرور الثابتة
PASSWORD = 'asdasd1428A'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='كلمة المرور خاطئة')
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_ip = request.remote_addr
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user_ip.replace('.', '_'))  # استبدال . بـ _ عشان اسم مجلد صالح
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    files = os.listdir(user_folder)
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    videos = [f for f in files if f.lower().endswith(('.mp4', '.mov'))]
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(user_folder, filename))
            return redirect(url_for('home'))
    
    return render_template('home.html', images=images, videos=videos, user_ip=user_ip)

@app.route('/download/<filename>')
def download(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_ip = request.remote_addr
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user_ip.replace('.', '_'))
    return send_from_directory(user_folder, filename)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
