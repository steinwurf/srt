#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

class MandatoryOptions(object):
	def __init__(self,options):
		self.options=options
	def __getattr__(self,name):
		call=getattr(self.options,name)
		def require(*args,**kwargs):
			value=call(*args,**kwargs)
			if value is None:
				raise RuntimeError('Mandatory option "{}" was set to "None"'.format(name))
			return value
		return require
