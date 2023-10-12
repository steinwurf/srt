#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import contextlib
import re
import sys
def open_for_writing(filename):
	if sys.version_info.major>=3:
		return open(filename,"w",newline="\n")
	else:
		return open(filename,"wb")
@contextlib.contextmanager
def rewrite_file(filename):
	class Content:
		def __init__(self):
			self.content=None
		def regex_replace(self,pattern,replacement):
			updated,count=re.subn(pattern=pattern,repl=replacement,string=self.content)
			if count==0:
				raise RuntimeError("Rewrite failed in {}. Pattern {} not ""found in file.\nContent:\n{}".format(filename,pattern,self.content))
			self.content=updated
	content=Content()
	flag="rU"if sys.version_info.major<3 else"r"
	with open(filename,flag)as f:
		content.content=f.read()
	yield content
	with open_for_writing(filename)as f:
		f.write(content.content)
