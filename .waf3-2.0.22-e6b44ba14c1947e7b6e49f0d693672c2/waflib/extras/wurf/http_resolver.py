#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import hashlib
class HttpResolver(object):
	def __init__(self,url_download,dependency,source,cwd):
		self.url_download=url_download
		self.dependency=dependency
		self.source=source
		self.cwd=cwd
	def resolve(self):
		self.dependency.current_source=self.source
		source_hash=hashlib.sha1(self.source.encode("utf-8")).hexdigest()[:6]
		folder_name="http-"+source_hash
		folder_path=os.path.join(self.cwd,folder_name)
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)
		if self.dependency.filename:
			filename=self.dependency.filename
		else:
			filename=None
		file_path=self.url_download.download(cwd=folder_path,source=self.source,filename=filename)
		assert os.path.isfile(file_path),"We should have a valid path here!"
		return file_path
