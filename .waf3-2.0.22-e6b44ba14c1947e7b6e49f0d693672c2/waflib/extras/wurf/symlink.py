#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import sys
import subprocess
from.error import RelativeSymlinkError
def create_symlink(from_path,to_path,overwrite=False,relative=False):
	if overwrite and os.path.lexists(path=to_path):
		_remove_symlink(path=to_path)
	is_directory=os.path.isdir(from_path)
	if relative:
		parent_dir=os.path.dirname(to_path)
		from_path=os.path.relpath(from_path,start=parent_dir)
	if sys.platform=="win32":
		_win32_create_symlink(from_path=from_path,to_path=to_path,is_directory=is_directory,is_relative=relative,)
	else:
		_unix_create_symlink(from_path=from_path,to_path=to_path)
def _remove_symlink(path):
	if sys.platform=="win32"and os.path.isdir(path):
		os.rmdir(path)
	else:
		os.unlink(path)
def _unix_create_symlink(from_path,to_path):
	os.symlink(from_path,to_path)
def _win32_create_symlink(from_path,to_path,is_directory,is_relative):
	try:
		_win32_py3_create_symlink(from_path,to_path,is_directory,is_relative)
	except(OSError,NotImplementedError,AttributeError):
		if is_relative:
			raise RelativeSymlinkError
		_win32_create_link(from_path,to_path,is_directory)
def _win32_create_link(from_path,to_path,is_directory):
	cmd=["mklink"]
	if is_directory:
		cmd+=["/J"]
	else:
		cmd+=["/H"]
	cmd+=['"{}"'.format(to_path.replace("/","\\")),'"{}"'.format(from_path.replace("/","\\")),]
	subprocess.check_output(" ".join(cmd),stderr=subprocess.STDOUT,shell=True)
def _win32_py3_create_symlink(from_path,to_path,is_directory,is_relative):
	os.symlink(src=from_path,dst=to_path,target_is_directory=is_directory)
