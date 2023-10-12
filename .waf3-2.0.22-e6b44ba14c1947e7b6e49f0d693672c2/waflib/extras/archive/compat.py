#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import sys
IS_PY2=sys.version_info[0]==2
if IS_PY2:
	def is_string(obj):
		return isinstance(obj,basestring)
else:
	def is_string(obj):
		return isinstance(obj,str)
