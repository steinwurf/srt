#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

from waflib.Configure import conf
from waflib.Errors import WafError
from waflib import Logs
from waflib import Context
from.import waf_resolve_context
from.import virtualenv
from.import rewrite
def extend_context(f):
	setattr(Context.Context,f.__name__,f)
	return f
@conf
def dependency_path(ctx,name):
	return waf_resolve_context.dependency_cache[name]["path"]
@conf
def dependency_node(ctx,name):
	return ctx.root.find_node(str(ctx.dependency_path(name)))
@conf
def has_dependency_path(ctx,name):
	return name in waf_resolve_context.dependency_cache
@conf
def is_toplevel(self):
	return self.srcnode==self.path
@conf
def recurse_dependencies(ctx):
	try:
		logfile=ctx.logger.handlers[0].baseFilename
	except Exception:
		logfile=None
	for name,dependency in waf_resolve_context.dependency_cache.items():
		if not dependency["recurse"]:
			Logs.debug("resolve: Skipped recurse {} cmd={}".format(name,ctx.cmd))
			continue
		path=dependency["path"]
		Logs.debug("resolve: recurse {} cmd={}, path={}".format(name,ctx.cmd,path))
		try:
			ctx.recurse([str(path)],once=False,mandatory=False)
		except WafError as e:
			msg='Recurse "{}" for "{}" failed with: {}'.format(name,ctx.cmd,e.msg)
			if logfile:
				msg="{}\n(complete log in {})".format(msg,logfile)
			else:
				msg="{}\n(run with -v for more information)".format(msg)
			raise WafError(msg=msg,ex=e)
@extend_context
def create_virtualenv(ctx,cwd=None,env=None,name=None,overwrite=True,system_site_packages=False):
	return virtualenv.VirtualEnv.create(ctx=ctx,log=Logs,cwd=cwd,env=env,name=name,overwrite=overwrite,system_site_packages=system_site_packages,)
@conf
def rewrite_file(ctx,filename):
	return rewrite.rewrite_file(filename=filename)
