from django.shortcuts import render
from django.http import HttpResponse

import simple_login.models

import json

def toplevel(request):
    return HttpResponse("goliath online")

def authn(request):
    if not request.user.is_authenticated():
        return HttpResponse("Unknown authentication credentials.", status=401)

    # XXX - We shouldn't be reaching backwards into the User Profile here.
    profile = simple_login.models.UserProfile.objects.get(user=request.user)
    role = profile.role

    if not role:
        return HttpResponse("No role attached to user.", status=401)

    body = json.dumps({"role": role.uri})

    return HttpResponse(content=body, content_type="application/json")
