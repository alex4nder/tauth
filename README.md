tauth - transparent authentication and authorization
----------------------------------------------------

High-level Requirements/Structure/Musings
-----------------------------------------

- What's being described here is a slightly more general version of
  what AWS has done with their IAM authentication/authorization package.

- Internal namespaced URIs are used to identify resources:
  - A user/role is referred to internally via a namespaced-URI.  This URI,
	along with any pertinent details of the authentication process, is
	what is passed between the authorization and authentication layers.

  - All resources being authorized against are referred by an internal,
	namespaced, URI.

  - This is very similar to existing industry approaches (e.g. Amazon's
	ARN).

- This system has a requirement to support internal and external
  authentication schemes (e.g. OpenID, OAuth*, SAML), and map
  (potentially federated) authentication into internally described
  users/roles.

- The authentication process is fundamentally separated from the
  authorization process.  These steps /can/ both happen inside one
  application, but they're separate loosely-coupled phases.

- The system is designed around supporting HTTP, but shouldn't block being
  extended to other protocols.

- A HTTP request must be able to be authenticated using potentially numerous
  different methods, e.g:
  - Different types of session cookies (e.g. django sessions).
  - HTTP Digest
  - AWSv4 Signatures
  - Other unknown/future request signing methods.

- Having support for multiple authentication schemes for a single
  service allows that service to support many types of clients
  (e.g. curl/CLI, single-page app, Rails/Django).  This is something
  that AWS's services have problems supporting.

- Authentication can/should happen entirely at the front-end request
  (e.g.  in nginx load balancer):
  - Helps mitigate/manage DoS attacks, as the request is authenticated
	before it is dispatched into any routing fabric/back end.

  - Internal services can assume that all requests against them have
	been authenticated.

- Authorization /can/ happen directly in/near the front-end, for wrapping
  simple requests and legacy services, e.g.:

  - HTTP GET request against a static asset.
  - graphite

- For more complicated authorization cases (e.g. where
  service-specific context is needed) an authorization service
  location would be provided along-side the authenticated request.
  This location would be used by the backend service to authorize
  the request.

Experimental/Initial Implementation Strategy
--------------------------------------------

Currently nginx is the de facto leader of the open-source load
balancer/request router herd.  It supports reverse-proxying to most
(all?) server-side web application frameworks/tools.  It also has an
extremely powerful and high-performance extension framework powered
by Lua/LuaJIT.

By implementing authentication (and simple authorization) in Lua and
running them inside nginx, it's possible to perform authentication
(and in some cases, full authorization) before the incoming request
leaves the reverse-proxy.

Multiple concurrent nginx instances can support authentication and
authorization by communicating with outside database/directories
(e.g. PostgreSQL, OpenLDAP).

For more complicated authorization cases, that require detailed
information provided by the backend service, the authorization
request can be made by the backend service.

authn/authz Server Requirements
-------------------------------

- authn servers:
  - MUST respond with a JSON body.
  - A 200 status MUST be returned only if the contents of the authn request was authenticated, it MUST NOT be returned otherwise.
  - If a 200 status is returned, role_uri and authz_url MUST be included in the JSON body.
  - authz_urls MUST NOT include query parameters.  The authz clients should be able to expect to append a query string (include ?) without having to parse authz_url.

- authz servers:
  - MUST respond with a JSON body.
  - A 200 status MUST be returned only if the contents of the authz request was authorized, it MUST NOT be returned otherwise.
