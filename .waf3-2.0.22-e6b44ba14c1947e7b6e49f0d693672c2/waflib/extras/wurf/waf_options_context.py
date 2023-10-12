#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import sys
from waflib import Context
from waflib import Options
from waflib import Logs
from.import registry
from.import waf_conf
class WafOptionsContext(Options.OptionsContext):
	def __init__(self,**kw):
		super(WafOptionsContext,self).__init__(**kw)
		self.waf_options=None
		self.wurf_options=None
		self.resolve_options_group=self.add_option_group("Resolve options")
		self.resolve_options_group.add_option("--no_resolve",default=False,action="store_true")
		self.resolve_options_group.add_option("--skip_internal",default=False,action="store_true")
	def execute(self):
		self.srcnode=self.path
		self.registry=registry.options_registry(ctx=self,git_binary="git")
		bldnode=self.path.make_node("build")
		bldnode.mkdir()
		log_path=os.path.join(bldnode.abspath(),"options.log")
		self.logger=Logs.make_logger(path=log_path,name="options")
		self.logger.debug("wurf: Options execute")
		resolve="--no_resolve"not in sys.argv
		skip_internal="--skip_internal"in sys.argv
		ctx=Context.create_context("resolve",resolve=resolve,skip_internal=skip_internal)
		try:
			ctx.execute()
		finally:
			ctx.finalize()
		if resolve:
			self.wurf_options=ctx.registry.require("options")
			self.waf_options=self.wurf_options.unknown_args
		else:
			self.waf_options=sys.argv
		self.load("wurf.waf_standalone_context")
		waf_conf.recurse_dependencies(self)
		handlers=self.logger.handlers[:]
		for handler in handlers:
			handler.close()
			self.logger.removeHandler(handler)
		super(WafOptionsContext,self).execute()
	def is_toplevel(self):
		return self.srcnode==self.path
	def parse_args(self,_args=None):
		assert _args is None
		try:
			if self.wurf_options:
				source_group=self.wurf_options.parser._optionals
				for action in source_group._group_actions:
					self.resolve_options_group.add_option(action.option_strings[0],action="store_true"if action.nargs==0 else"store",help=action.help,)
		finally:
			super(WafOptionsContext,self).parse_args(_args=self.waf_options)
