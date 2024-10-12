from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

socketio = SocketIO(app)


# Ruta principal para servir la página
@app.route('/')
def index():#valiendo verga
    return render_template('index.html')



if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
