#!/usr/bin/env python
from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/echoback')
def echoback():
    role_uri = request.headers["X-Tauth-Role-Uri"]
    authz_url = request.headers["X-Tauth-Authz-Url"]

    r = requests.get(authz_url,
                     params={
            'role_uri': role_uri,
            'action_uri': 'tauth:simple_login:actions:access',
            'resource_uri': 'tauth:simple_login:resources:echo',
            })

    if r.status_code != 200:
        return Response("forbidden", status=403)

    res = []

    for k, v in request.headers.iteritems():
        res.append("%s: %s" % (k, v))
    
    return Response("\n".join(res), mimetype="text/plain")

if __name__ == '__main__':
    app.run(debug=True, port=8484)
