package.path = package.path .. ';../../?.lua'

ta = require("tauth.nginx")

local cc = ta.authn.passthrough_check("/tauth/authn")
ta.authn.add_handler("django", cc)
