from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/',methods=["GET","POST"])
@cross_origin()
def query_example():
    with open('GuildFiles/Jarvis_dot_exe.json', encoding='utf8') as data:
        response = json.load(data)
        data.close()
    return response
app.run(debug=True, port=5000)