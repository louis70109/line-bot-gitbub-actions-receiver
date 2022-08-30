import os

if os.getenv('PY_ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from controller.line_controller import LineIconSwitchController

app = Flask(__name__)
CORS(app)

api = Api(app)

@app.get("/")
def check():
    return {"message": "Hello World!"}

api.add_resource(LineIconSwitchController, '/webhooks/line')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=True)
