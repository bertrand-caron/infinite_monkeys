from sys import stderr
from typing import Any
from flask import Flask, request, jsonify, redirect

APPLICATION = Flask(__name__)

@APPLICATION.route('/update')
def update():
    import test
    import testAPI

    search = request.args.get('sentence')

    testAPI.main(search)
    test.main()
    return redirect('http://40.65.189.31/D3')

if __name__ == "__main__":
    APPLICATION.run(threaded=True, processes=8)
