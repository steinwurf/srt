#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
from.symlink import create_symlink
from.error import RelativeSymlinkError
class CreateSymlinkResolver(object):
	def __init__(self,resolver,dependency,symlinks_path,ctx):
		self.resolver=resolver
		self.dependency=dependency
		self.symlinks_path=symlinks_path
		self.ctx=ctx
		assert os.path.isabs(self.symlinks_path)
	def resolve(self):
		path=self.resolver.resolve()
		if not path:
			return path
		if self.dependency.is_symlink:
			path=self.dependency.real_path
		link_path=os.path.join(self.symlinks_path,self.dependency.name)
		try:
			self.ctx.to_log("wurf: CreateSymlinkResolver {} -> {}".format(link_path,path))
			try:
				create_symlink(from_path=path,to_path=link_path,overwrite=True,relative=True)
			except RelativeSymlinkError:
				self.ctx.to_log("wurf: Using relative symlink failed - fallback ""to absolute.")
				create_symlink(from_path=path,to_path=link_path,overwrite=True,relative=False)
		except Exception as ex:
			msg="Symlink creation failed for: {}\n".format(self.dependency.name)
			if hasattr(ex,"output"):
				msg+=str(ex.output)
			self.ctx.logger.debug(msg,exc_info=True)
			return path
		self.dependency.is_symlink=True
		self.dependency.real_path=path
		return link_path
	def __repr__(self):
		return"%s(%r)"%(self.__class__.__name__,self.__dict__)
