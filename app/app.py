import os

from flask import Flask, Response, request

import worker


ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=["POST"])
@app.route("/<string:path>", methods=["POST"])
@app.route("/<path:path>", methods=["POST"])
def collect(path):
    token = request.json.get("access_token")
    if (not ACCESS_TOKEN) or token == ACCESS_TOKEN:
        data = request.json.get("data")
        if data:
            worker.write_to_db.delay(data)
        return Response("{}", status=200)
    return Response("{}", status=400)
