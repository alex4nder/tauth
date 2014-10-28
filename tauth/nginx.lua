local cjson = require("cjson")
local http = require("resty.http")

local _M = {}

_M.authz = {}
_M.authn = {}

function _M.sanitize_request()
   -- XXX - If a request has more than N headers, we should probably
   -- just drop it, rather than trying to loop through them all.

   for k, v in pairs(ngx.req.get_headers(0)) do
      -- Zap any incoming requests pre-populated with
      -- anything that looks like a tauth header.
      if string.find(k:lower(), "x-tauth", 1, true) == 1 then
	 ngx.req.clear_header(k)
      end
   end
end

function _M.authn.passthrough_check(location)
   local _o = {}

   _o._location = location

   function _o:lookup ()
      -- This capture to an internal location will forward all headers, much
      -- like a normal 'auth_request'.

      res = ngx.location.capture(self._location,
				 {method=ngx.HTTP_GET, body=nil})

      if res.status ~= 200 then
	 return nil
      end

      -- XXX - Clearly this is too raw of an interface.
      local info = cjson.decode(res.body)
      return info
   end

   return _o
end

_M._authn_handlers = {}
function _M.authn.add_handler (name, handler)
   _M._authn_handlers[name] = handler
   return true
end

function _M.authn.lookup()
   for name, handler in pairs(_M._authn_handlers) do
      local info = handler:lookup()
      if info then
	 return info
      end
   end

   return nil
end

function _M.authn.check()
   _M.sanitize_request()

   local info = _M.authn.lookup()

   -- TODO - If we fall through, and at least one of the authn
   -- services proposed a way to get access to valid credentials, we should
   -- forward that on to the client (maybe via redirect?).

   if not info then
      ngx.exit(ngx.HTTP_UNAUTHORIZED)
      return nil
   end

   if not info.role_uri or not info.authz_url then
      ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
      return nil
   end

   for k, v in pairs(info) do
      -- Values of nested JSON objects aren't supported.
      if type(v) ~= "table" then
	 -- XXX - The substitution is probably (definitely?)
	 -- naive.  This will have to evolve.
	 local h = "X-Tauth-" .. string.gsub(k, "_", "-")
	 ngx.req.set_header(h, v)
      end
   end

   return info
end

function _M.authz.check(resource_uri, action_uri)
   -- TODO - Extend the handler API to allow us to check authn and
   -- authz in one request, if a remote authority supports it.

   local info = _M.authn.check()
   if not info then
      return
   end

   local httpc = http.new()
   local authz_url = info.authz_url .. "?" .. ngx.encode_args({role_uri = info.role_uri,
							       resource_uri = resource_uri,
							       action_uri = action_uri})

   local res, err = httpc:request_uri(authz_url, {method="GET"})

   if not res then
      ngx.log(ngx.ERR, "tauth authz: " .. err)
      return ngx.exit(ngx.HTTP_SERVICE_UNAVAILABLE)
   end

   if res["status"] ~= 200 then
      return ngx.exit(ngx.HTTP_FORBIDDEN)
   end

   return ngx.exit(ngx.OK)
end

return _M
