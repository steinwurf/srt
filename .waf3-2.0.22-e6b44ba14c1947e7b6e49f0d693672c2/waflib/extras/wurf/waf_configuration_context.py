#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
from waflib import Context
from waflib import Utils
from waflib import Logs
from waflib.Configure import ConfigurationContext
from.symlink import create_symlink
class WafConfigurationContext(ConfigurationContext):
	def __init__(self,**kw):
		super(WafConfigurationContext,self).__init__(**kw)
	def init_dirs(self):
		super(WafConfigurationContext,self).init_dirs()
		link_path=os.path.join(self.path.abspath(),"build_current")
		try:
			create_symlink(from_path=self.bldnode.abspath(),to_path=link_path,overwrite=True)
		except Exception:
			Logs.warn("Could not create the 'build_current' symlink in ""{}".format(self.path.abspath()))
	def execute(self):
		if"configure"not in Context.g_module.__dict__:
			Context.g_module.configure=Utils.nada
		super(WafConfigurationContext,self).execute()
	def pre_recurse(self,node):
		super(WafConfigurationContext,self).pre_recurse(node)
		if self.is_toplevel():
			self.recurse_dependencies()
