#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import hashlib
class ArchiveResolver(object):
	def __init__(self,archive_extractor,resolver,cwd):
		self.archive_extractor=archive_extractor
		self.resolver=resolver
		self.cwd=cwd
	def resolve(self):
		path=self.resolver.resolve()
		assert os.path.isfile(path)
		extract_hash=hashlib.sha1(path.encode("utf-8")).hexdigest()[:6]
		extract_folder="extract-"+extract_hash
		extract_path=os.path.join(self.cwd,extract_folder)
		self.archive_extractor(path=path,to_path=extract_path)
		return extract_path
