from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse

import simple_login.models
import models

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

    response = {}
    response["role_uri"] = role.uri
    response["authz_url"] = request.build_absolute_uri(reverse("tauth-authz"))
    response["authn_certainty"] = 50


    body = json.dumps(response)
    return HttpResponse(content=body, content_type="application/json")

def authz(request):
    # XXX - We don't require that this request be authenticated,
    # because it's being made by a client that (most likely) had
    # no part in checking the original authz of the request.
    #
    # Authentication requests for this query mechanism can be made
    # outside of django at the gateway (e.g. based on some ACL).

    if request.method != "GET":
        return HttpResponse("Invalid request method.", status=400)

    def param(n):
        return request.GET.get(n, None)

    found = False

    role_uri = param("role_uri")
    if not role_uri:
        return HttpResponse("role_uri is required.", status=400)

    try:
        role = models.Role.objects.get(uri=role_uri)
    except models.Role.DoesNotExist:
        return HttpResponse("unknown role_uri.", status=404)

    resource_uri = param("resource_uri")

    if not resource_uri:
        return HttpResponse("resource_uri is required.", status=400)

    try:
        resource = models.Resource.objects.get(uri=resource_uri)
    except models.Resource.DoesNotExist:
        return HttpResponse("unknown resource_uri.", status=404)

    action_uri = param("action_uri")

    why = None

    # Step through all of the allows first, then the denies.
    for e in (models.Permission.ALLOW, models.Permission.DENY):
        perms = models.Permission.objects.filter(role=role, resource=resource, effect=e)

        for p in perms:
            # If this permission has an action, and it doesn't match what was request
            # then it doesn't affect the decision making.
            if p.action_uri and p.action_uri != action_uri:
                pass
            else:
                why = p

    response = {}

    # We didn't find anything, punt.
    if why == None:
        response["message"] = "no applicable permissions found"
        status = 403
    else:
        if why.effect == models.Permission.DENY:
            response["message"] = "request denied"
            status = 403
        else:
            status = 200
            response["message"] = "request allowed"

        response["action_uri"] = why.action_uri
        response["role_uri"] = why.role.uri
        response["resource_uri"] = why.resource.uri

    body = json.dumps(response)

    return HttpResponse(content=body, content_type="application/json", status=status)
