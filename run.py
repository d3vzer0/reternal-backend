from app import app, socketio

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=app.config['FLASK_PORT'])
