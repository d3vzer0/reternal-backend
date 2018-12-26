from app import app

if __name__ == "__main__":
    #socketio.run(app, debug=True, host=app.config['SERVER_ADDRESS'], port=5000)
    app.run(debug=True, port=5000)
