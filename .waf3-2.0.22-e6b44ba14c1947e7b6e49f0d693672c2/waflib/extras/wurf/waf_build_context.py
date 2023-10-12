#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

from waflib.Build import BuildContext
class WafBuildContext(BuildContext):
	def execute_build(self):
		self.recurse_dependencies()
		super(WafBuildContext,self).execute_build()
