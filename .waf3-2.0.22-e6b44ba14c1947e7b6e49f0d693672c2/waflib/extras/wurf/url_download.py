#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import cgi
import os
from.compat import IS_PY2
if IS_PY2:
	from urllib2 import urlopen
	from urlparse import urlparse
else:
	from urllib.request import urlopen
	from urllib.parse import urlparse
class UrlDownload(object):
	def _url_filename(self,url):
		parsed=urlparse(url)
		if not parsed.path:
			return None
		filename=os.path.basename(parsed.path)
		_,extension=os.path.splitext(filename)
		if not extension:
			return None
		else:
			return filename
	def _response_filename(self,response):
		header=response.info().get("Content-Disposition","")
		if not header:
			return None
		_,params=cgi.parse_header(header)
		return params.get("filename",None)
	def download(self,cwd,source,filename=None):
		response=urlopen(url=source)
		if not filename:
			filename=self._url_filename(source)
		if not filename:
			filename=self._response_filename(response)
		assert filename
		assert os.path.isdir(cwd)
		filepath=os.path.join(cwd,filename)
		CHUNK=16*1024
		with open(filepath,"wb")as f:
			while True:
				chunk=response.read(CHUNK)
				if not chunk:
					break
				f.write(chunk)
		return filepath
