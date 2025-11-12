from flask import Flask
app=None

# App description and config
def create_app():
    app=Flask(__name__)
    app.debug=True
    return app 