local cjson = require("cjson")

local _M = {}

_M.authz = {}
_M.authn = {}

function _M.sanitize_request()
   -- XXX - If a request has more than N headers, we should probably
   -- just drop it, rather than trying to loop through them all.

   for k, v in pairs(ngx.req.get_headers(0)) do
      -- Zap any incoming requests pre-poulated with
      -- anything that looks like a tauth header.
      if string.find(k:lower(), "x-tauth", 1, true) == 1 then
	 ngx.req.clear_header(k)
      end
   end
end

function _M.authn.passthrough_check(location)
   local _o = {}

   _o._location = location

   function _o:check ()
      -- This capture to an internal location will forward all headers, much
      -- like a normal 'auth_request'.

      res = ngx.location.capture(self._location, { method=ngx.HTTP_GET, body=nil } )
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

function _M.authn.check()
   _M.sanitize_request()

   for name, handler in pairs(_M._authn_handlers) do
      local info = handler:check()
      if info then
	 -- TODO - We need to be able to attach additional headers here,
	 -- based on arbitrary responses from the authn server.
	 ngx.req.set_header("X-Tauth-Role", info.role)
	 return info
      end

      -- TODO - If we fall through, and at least one of the authn
      -- services proposed a way to get access to valid credentials, we should
      -- forward that on to the client (maybe via redirect?).
   end

   return nil
end

function _M.authz.check_by_uri (uri)
   -- TODO - Extend the handler API to allow us to check authn and
   -- authz in one request, if a remote authority supports it.

   local info = _M.authn.check()

   if not info or not info.role then
      return ngx.exit(ngx.HTTP_UNAUTHORIZED)
   end

   -- TODO - We still need to check authorization here.

   return ngx.exit(ngx.OK)
end

return _M
