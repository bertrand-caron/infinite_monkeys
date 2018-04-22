from sys import stderr
from typing import Any
from flask import Flask, request, jsonify

APPLICATION = Flask(__name__)

@APPLICATION.route('/update')
def update():
    import test
    import testAPI

    testAPI.main()
    test.main()

if __name__ == "__main__":
    APPLICATION.run(threaded=True, processes=8)
