from flask import Flask
import webbrowser
from threading import Timer

app = Flask(__name__)

@app.route('/')
def home():
    return "Mon projet Flask fonctionne sur Linux Mint !"

def open_browser():
    webbrowser.open('http://localhost:8000')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, port=8000)
