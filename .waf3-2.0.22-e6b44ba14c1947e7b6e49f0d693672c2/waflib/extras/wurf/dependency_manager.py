#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import json
from.dependency import Dependency
from.error import WurfError
class DependencyManager(object):
	def __init__(self,registry,dependency_cache,ctx,options,skip_internal):
		self.registry=registry
		self.dependency_cache=dependency_cache
		self.ctx=ctx
		self.options=options
		self.skip_internal=skip_internal
		self.seen_dependencies={}
		self.post_resolve_actions=[]
	def load_dependencies(self,path,mandatory=False):
		resolve_path=os.path.join(path,"resolve.json")
		if not os.path.isfile(resolve_path):
			if mandatory:
				raise WurfError("Mandatory resolve.json not found here: {}".format(resolve_path))
			else:
				return
		with open(resolve_path,"r")as resolve_file:
			resolve_json=json.load(resolve_file)
		for dependency in resolve_json:
			self.add_dependency(**dependency)
	def add_dependency(self,**kwargs):
		dependency=Dependency(**kwargs)
		if self.__skip_dependency(dependency):
			return
		self.options.add_dependency(dependency)
		with self.registry.provide_temporary()as tmp:
			tmp.provide_value("dependency",dependency)
			resolver=self.registry.require("dependency_resolver")
		path=resolver.resolve()
		if not path:
			return
		if dependency.recurse:
			self.ctx.recurse([str(path)],mandatory=False)
		self.dependency_cache[dependency.name]={"path":path,"recurse":dependency.recurse,}
	def __skip_dependency(self,dependency):
		if dependency.internal:
			if self.skip_internal:
				return True
			if not self.ctx.is_toplevel():
				return True
		if dependency.name in self.seen_dependencies:
			seen_dependency=self.seen_dependencies[dependency.name]
			if not dependency.override and seen_dependency.override:
				return True
			if dependency.override and not seen_dependency.override:
				raise WurfError("Overriding dependency:\n{}\n""added after non overriding dependency:\n{}".format(dependency,seen_dependency))
			if seen_dependency.sha1!=dependency.sha1:
				raise WurfError("SHA1 mismatch when adding:\n{}\n""the previous definition was:\n{}".format(dependency,seen_dependency))
			if not dependency.optional and seen_dependency.optional:
				self.seen_dependencies[dependency.name]=dependency
				if dependency.name not in self.dependency_cache:
					return False
			return True
		self.seen_dependencies[dependency.name]=dependency
		return False
	def post_resolve(self):
		for action in self.post_resolve_actions:
			action(dependency_manager=self)
	def add_post_resolve_action(self,action):
		self.post_resolve_actions.append(action)
