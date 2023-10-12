#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import sys
import hashlib
from.directory import remove_directory
class VirtualEnv(object):
	def __init__(self,env,cwd,path,ctx):
		self.env=env
		self.path=path
		self.cwd=cwd
		self.ctx=ctx
		if sys.platform=="win32":
			python_path=os.path.join(path,"Scripts")
		else:
			python_path=os.path.join(path,"bin")
		self.env["PATH"]=os.path.pathsep.join([python_path,env["PATH"]])
	def run(self,cmd,cwd=None):
		if not cwd:
			cwd=self.cwd
		ret=self.ctx.exec_command(cmd,cwd=cwd,env=self.env,stdout=None,stderr=None)
		if ret!=0:
			self.ctx.fatal('Exec command "{}" failed!'.format(cmd))
	def __enter__(self):
		return self
	def __exit__(self,type,value,traceback):
		remove_directory(path=self.path)
	@staticmethod
	def check_venv():
		try:
			import ensurepip
			assert ensurepip
			return True
		except ImportError:
			return False
	@staticmethod
	def check_virtualenv():
		try:
			import virtualenv
			assert virtualenv
			return True
		except ImportError:
			return False
	@staticmethod
	def create(ctx,log,cwd=None,env=None,name=None,overwrite=True,system_site_packages=False,):
		python=sys.executable
		if not cwd:
			cwd=ctx.path.abspath()
		if cwd.startswith(os.path.join(ctx.path.abspath(),"build")):
			ctx.fatal("Cannot create virtualenv inside the build folder. ""Virtualenv create symlinks to files that will be ""deleted with 'waf clean'.")
		if not env:
			env=dict(os.environ)
		if"PYTHONPATH"in env:
			del env["PYTHONPATH"]
		if not name:
			unique=hashlib.sha1(python.encode("utf-8")).hexdigest()[:6]
			name="virtualenv-{}".format(unique)
		path=os.path.join(cwd,name)
		if os.path.isdir(path)and overwrite:
			remove_directory(path=path)
		if os.path.isdir(path):
			return VirtualEnv(env=env,path=path,cwd=cwd,ctx=ctx)
		if VirtualEnv.check_venv():
			cmd=[python,"-m","venv",name]
		elif VirtualEnv.check_virtualenv():
			cmd=[python,"-m","virtualenv",name]
		else:
			ctx.fatal("Cannot create virtual environment due to missing Python support. ""If on Debian/Ubuntu virtualenv support can be added by ""running 'apt install python3-venv'.")
		if system_site_packages:
			cmd+=["--system-site-packages"]
		ctx.cmd_and_log(cmd,cwd=cwd,env=env)
		return VirtualEnv(env=env,path=path,cwd=cwd,ctx=ctx)
