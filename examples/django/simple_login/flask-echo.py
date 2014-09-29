#!/usr/bin/env python
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/echoback')
def echoback():
    res = []

    for k, v in request.headers.iteritems():
        res.append("%s: %s" % (k, v))
    
    return Response("\n".join(res), mimetype="text/plain")

if __name__ == '__main__':
    app.run(debug=True, port=8484)
