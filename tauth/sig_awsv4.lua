local _M = {}

crypto = require("crypto")

local hmac = crypto.hmac
local digest = crypto.digest

function _h (k, v)
   return hmac.digest("sha256", v, k, true)
end

function _M.signingKey(secret, dateStamp, regionName, serviceName)
   return _h(_h(_h(_h("AWS4" .. secret, dateStamp), regionName), serviceName), "aws4_request")
end

-- local key = "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"
-- local dateStamp = "20120215"
-- local regionName = "us-east-1"
-- local serviceName = "iam"
-- 
-- print(signingKey(key, dateStamp, regionName, serviceName))

return _M
