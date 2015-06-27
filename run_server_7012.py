# -*- coding:utf-8 -*-

import web
import os
import json
from guagua import Guagua

web.config.debug = True

urls = (
		'/guagua/.*', 'Guagua',
		)

def notfound():
	# web.header('Content-Type', 'application/json')
	# return json.dumps({"data":[]})
	return web.notfound(json.dumps({"data":[]}))

def internalerror():
	return web.internalerror(json.dumps({"data":[]}))

app_root = os.path.dirname(__file__)

if __name__ == '__main__':
	app = web.application(urls, globals())
	app.notfound = notfound
	app.internalerror = notfound
	app.run()
