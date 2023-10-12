#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import hashlib
from.directory import copy_directory
from.directory import remove_directory
from.error import WurfError
class PostResolveRun(object):
	def __init__(self,resolver,ctx,run,cwd):
		self.resolver=resolver
		self.ctx=ctx
		self.run=run
		self.cwd=cwd
	def resolve(self):
		path=self.resolver.resolve()
		if os.path.isfile(path):
			path=os.path.dirname(path)
		hash_data=str(self.run)+path
		run_hash=hashlib.sha1(hash_data.encode("utf-8")).hexdigest()[:6]
		folder_name="run-"+run_hash
		run_path=os.path.join(self.cwd,folder_name)
		if os.path.isdir(run_path):
			return run_path
		try:
			copy_directory(path=path,to_path=run_path)
			self.ctx.cmd_and_log(cmd=self.run,cwd=run_path)
		except WurfError:
			if os.path.isdir(run_path):
				remove_directory(path=run_path)
			raise
		return run_path
