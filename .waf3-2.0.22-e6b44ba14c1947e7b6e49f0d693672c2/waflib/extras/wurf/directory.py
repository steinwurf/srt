#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import shutil
import stat
import os
def copy_directory(path,to_path):
	try:
		path=unicode(path)
		to_path=unicode(to_path)
	except NameError:
		pass
	shutil.copytree(src=path,dst=to_path,symlinks=True)
def remove_directory(path):
	try:
		path=unicode(path)
	except NameError:
		pass
	for root,dirs,files in os.walk(path,topdown=False):
		for name in files:
			filename=os.path.join(root,name)
			if not os.path.islink(filename):
				os.chmod(filename,stat.S_IWUSR)
			os.remove(filename)
		for name in dirs:
			dir=os.path.join(root,name)
			if os.path.islink(dir):
				os.unlink(dir)
			else:
				os.rmdir(dir)
	os.rmdir(path)
