import urllib2
import urllib
import urlparse
import json
import copy

KAMU_API_BASE = "http://localhost:8000/api/v1/"

class FlatApiProxy(object):
	def __init__(self, base_url):
		self.__base_url = urlparse.urlsplit(base_url)
	
	def _proxy_call(self, method, **kwargs):
		# How pythonic...
		url = list(self.__base_url)
		url[2] += method
		url[3] = urllib.urlencode(kwargs)
		url = urlparse.urlunsplit(url)
		return json.load(urllib2.urlopen(url))
	
	def __getattr__(self, method):
		func = lambda **kwargs: self._proxy_call(method, **kwargs)
		return func

kamu_api = FlatApiProxy(KAMU_API_BASE)
