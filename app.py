from flask import Flask, render_template, redirect, url_for
from background import run_background

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    run_background()
    return redirect(url_for('home'))  # Redirect back to homepage

if __name__ == '__main__':
    app.run(debug=True)
