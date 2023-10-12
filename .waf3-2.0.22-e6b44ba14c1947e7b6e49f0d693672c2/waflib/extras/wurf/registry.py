#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import argparse
import os
import json
import hashlib
import inspect
import collections
from.compat import IS_PY2
from.git_resolver import GitResolver
from.path_resolver import PathResolver
from.context_msg_resolver import ContextMsgResolver
from.dependency_manager import DependencyManager
from.check_optional_resolver import CheckOptionalResolver
from.on_active_store_path_resolver import OnActiveStorePathResolver
from.on_passive_load_path_resolver import OnPassiveLoadPathResolver
from.try_resolver import TryResolver
from.list_resolver import ListResolver
from.git_checkout_resolver import GitCheckoutResolver
from.existing_checkout_resolver import ExistingCheckoutResolver
from.git_semver_resolver import GitSemverResolver
from.git_url_parser import GitUrlParser
from.git_url_rewriter import GitUrlRewriter
from.git import Git
from.options import Options
from.config_file import ConfigFile
from.mandatory_options import MandatoryOptions
from.mandatory_resolver import MandatoryResolver
from.create_symlink_resolver import CreateSymlinkResolver
from.configuration import Configuration
from.store_lock_path_resolver import StoreLockPathResolver
from.store_lock_version_resolver import StoreLockVersionResolver
from.check_lock_cache_resolver import CheckLockCacheResolver
from.lock_cache import LockCache
from.semver_selector import SemverSelector
from.tag_database import TagDatabase
from.existing_tag_resolver import ExistingTagResolver
from.url_download import UrlDownload
from.http_resolver import HttpResolver
from.archive_resolver import ArchiveResolver
from.post_resolve_run import PostResolveRun
from.error import WurfError
class RegistryProviderError(WurfError):
	def __init__(self,name):
		self.name=name
		super(RegistryProviderError,self).__init__("Registry error: {} already added to registry".format(self.name))
class RegistryInjectError(WurfError):
	def __init__(self,provider_function,missing_provider):
		self.provider_function=provider_function
		self.missing_provider=missing_provider
		super(RegistryInjectError,self).__init__('Fatal error provider "{}" requires "{}"'.format(self.provider_function.__name__,self.missing_provider))
class RegistryCacheOnceError(WurfError):
	def __init__(self,provider_name,provider_function):
		self.provider_name=provider_name
		self.provider_function=provider_function
		super(RegistryCacheOnceError,self).__init__('Fatal error provider "{}" should only be cached once. The ''provided values passed to "{}" have changed since the object was '"initially cached.".format(self.provider_name,self.provider_function.__name__))
class Registry(object):
	class TemporaryValue:
		def __init__(self,registry):
			self.registry=registry
			self.provider_names=[]
		def __enter__(self):
			return self
		def provide_value(self,provider_name,value,override=False):
			self.provider_names.append(provider_name)
			self.registry.provide_value(provider_name=provider_name,value=value,override=override)
		def __exit__(self,type,value,traceback):
			for provider_name in self.provider_names:
				self.registry.remove(provider_name=provider_name)
	ShouldCache=collections.namedtuple("ShouldCache","name once")
	class CacheEntry(object):
		def __init__(self,once):
			self.once=once
			self.data={}
	providers={}
	cache_providers=set()
	def __init__(self,use_providers=True,use_cache_providers=True):
		self.registry={}
		self.cache={}
		if use_cache_providers:
			for s in Registry.cache_providers:
				self.cache_provider(provider_name=s.name,once=s.once)
		if use_providers:
			for k,v in Registry.providers.items():
				self.provide_function(k,v)
	def cache_provider(self,provider_name,once):
		assert provider_name not in self.cache
		self.cache[provider_name]=Registry.CacheEntry(once=once)
	def purge_cache(self):
		for provider_name in self.cache:
			self.cache[provider_name].data={}
	def __inject_arguments(self,provider_function):
		inject_arguments={}
		if IS_PY2:
			require_arguments=inspect.getargspec(provider_function)[0]
		else:
			require_arguments=inspect.getfullargspec(provider_function)[0]
		for argument in require_arguments:
			if argument=="registry":
				inject_arguments[argument]=self
				continue
			if argument not in self:
				raise RegistryInjectError(provider_function=provider_function,missing_provider=argument)
			inject_arguments[argument]=self.require(argument)
		return inject_arguments
	def __hash_arguments(self,arguments):
		hash_dict={}
		for k,v in arguments.items():
			if isinstance(v,(list,tuple,dict,set)):
				hash_dict[k]=hash(json.dumps(v,sort_keys=True))
			else:
				hash_dict[k]=hash(v)
		return hash(json.dumps(hash_dict,sort_keys=True))
	def provide_function(self,provider_name,provider_function,override=False):
		if not override and provider_name in self.registry:
			raise RegistryProviderError(provider_name)
		def call():
			inject_arguments=self.__inject_arguments(provider_function=provider_function)
			if provider_name in self.cache:
				key=self.__hash_arguments(inject_arguments)
				provider=self.cache[provider_name]
				try:
					return provider.data[key]
				except KeyError:
					if provider.once and len(provider.data)>0:
						raise RegistryCacheOnceError(provider_name,provider_function)
					result=provider_function(**inject_arguments)
					provider.data[key]=result
					return result
			else:
				result=provider_function(**inject_arguments)
				return result
		self.registry[provider_name]=call
		if provider_name in self.cache:
			self.cache[provider_name].data={}
	def provide_temporary(self):
		return Registry.TemporaryValue(registry=self)
	def provide_value(self,provider_name,value,override=False):
		if not override and provider_name in self.registry:
			raise RegistryProviderError(provider_name)
		def call():
			return value
		self.registry[provider_name]=call
	def require(self,provider_name):
		if inspect.isclass(provider_name):
			provider_name=provider_name.__name__
		call=self.registry[provider_name]
		return call()
	def remove(self,provider_name):
		if provider_name in self.cache:
			del self.cache[provider_name]
		del self.registry[provider_name]
	def __contains__(self,provider_name):
		return provider_name in self.registry
	@staticmethod
	def cache(func):
		Registry.cache_providers.add(Registry.ShouldCache(name=func.__name__,once=False))
		return func
	@staticmethod
	def cache_once(func):
		Registry.cache_providers.add(Registry.ShouldCache(name=func.__name__,once=True))
		return func
	@staticmethod
	def provide(func):
		if func.__name__ in Registry.providers:
			raise RegistryProviderError(func.__name__)
		Registry.providers[func.__name__]=func
		return func
@Registry.cache_once
@Registry.provide
def resolve_path(mandatory_options,waf_utils):
	resolve_path=mandatory_options.resolve_path()
	resolve_path=os.path.abspath(os.path.expanduser(resolve_path))
	waf_utils.check_dir(resolve_path)
	return resolve_path
@Registry.cache_once
@Registry.provide
def symlinks_path(mandatory_options,waf_utils):
	symlinks_path=mandatory_options.symlinks_path()
	symlinks_path=os.path.abspath(os.path.expanduser(symlinks_path))
	waf_utils.check_dir(symlinks_path)
	return symlinks_path
@Registry.cache
@Registry.provide
def dependency_path(git_url_rewriter,resolve_path,source,dependency,waf_utils):
	if dependency.resolver=="git":
		repo_url=git_url_rewriter.rewrite_url(url=source)
		repo_hash=hashlib.sha1(repo_url.encode("utf-8")).hexdigest()[:6]
		name=dependency.name+"-"+repo_hash
	else:
		source_hash=hashlib.sha1(source.encode("utf-8")).hexdigest()[:6]
		name=dependency.name+"-"+source_hash
	dependency_path=os.path.join(resolve_path,name)
	waf_utils.check_dir(dependency_path)
	return dependency_path
@Registry.cache_once
@Registry.provide
def git_url_parser():
	return GitUrlParser()
@Registry.cache_once
@Registry.provide
def git_url_rewriter(git_url_parser,git_protocol):
	return GitUrlRewriter(parser=git_url_parser,rewrite_protocol=git_protocol)
@Registry.cache_once
@Registry.provide
def parser():
	return argparse.ArgumentParser(description="Resolve Options",add_help=False,)
@Registry.cache_once
@Registry.provide
def dependency_cache():
	return collections.OrderedDict()
@Registry.cache_once
@Registry.provide
def lock_cache(configuration,options,project_path):
	if configuration.resolver_chain()==Configuration.RESOLVE_AND_LOCK:
		return LockCache.create_empty(options=options)
	elif configuration.resolver_chain()==Configuration.RESOLVE_FROM_LOCK:
		lock_path=os.path.join(project_path,Configuration.LOCK_FILE)
		return LockCache.create_from_file(lock_path=lock_path)
	else:
		raise WurfError("Lock cache not available for {} chain".format(configuration.resolver_chain()))
@Registry.cache_once
@Registry.provide
def options(parser,args,default_resolve_path,default_symlinks_path,config_file):
	supported_git_protocols=GitUrlRewriter.git_protocols.keys()
	if config_file.default_resolve_path:
		resolve_path=config_file.default_resolve_path
	else:
		resolve_path=default_resolve_path
	return Options(args=args,parser=parser,default_resolve_path=resolve_path,default_symlinks_path=default_symlinks_path,supported_git_protocols=supported_git_protocols,)
@Registry.cache_once
@Registry.provide
def config_file(ctx):
	return ConfigFile(ctx=ctx)
@Registry.cache_once
@Registry.provide
def mandatory_options(options):
	return MandatoryOptions(options=options)
@Registry.cache_once
@Registry.provide
def semver_selector(semver):
	return SemverSelector(semver=semver)
@Registry.cache_once
@Registry.provide
def tag_database(ctx):
	return TagDatabase(ctx=ctx)
@Registry.cache_once
@Registry.provide
def url_download():
	return UrlDownload()
@Registry.cache_once
@Registry.provide
def project_git_protocol(git,ctx,git_url_parser):
	try:
		parent_url=git.remote_origin_url(cwd=os.getcwd())
	except Exception as e:
		ctx.to_log("Exception when executing git.remote_origin_url: {}".format(e))
		return None
	try:
		url=git_url_parser.parse(parent_url)
		return url.protocol
	except Exception as e:
		ctx.to_log("Exception could not parse git URL {} error: {}".format(parent_url,e))
		return None
@Registry.cache_once
@Registry.provide
def git(git_binary,ctx):
	return Git(git_binary=git_binary,ctx=ctx)
@Registry.cache_once
@Registry.provide
def git_protocol(options,project_git_protocol):
	protocol=options.git_protocol()
	if not protocol:
		protocol=project_git_protocol
	if not protocol:
		protocol="https://"
	return protocol
@Registry.provide
def post_resolve(registry,current_resolver,dependency):
	resolver=current_resolver
	for resolve in dependency.post_resolve:
		with registry.provide_temporary()as temporary:
			temporary.provide_value("{}_command".format(resolve["type"]),resolve["command"])
			resolver=registry.require("post_resolve_{}".format(resolve["type"]))
		registry.provide_value(provider_name="current_resolver",value=resolver,override=True)
	return resolver
@Registry.provide
def user_path_resolver(mandatory_options,dependency):
	path=mandatory_options.path(dependency=dependency)
	dependency.resolver_action="user path"
	return PathResolver(dependency=dependency,path=path)
@Registry.provide
def post_resolve_run(current_resolver,ctx,run_command,dependency_path):
	return PostResolveRun(resolver=current_resolver,ctx=ctx,run=run_command,cwd=dependency_path)
@Registry.provide
def git_resolver(git,ctx,dependency,source,git_url_rewriter,dependency_path):
	return GitResolver(git=git,ctx=ctx,dependency=dependency,source=source,git_url_rewriter=git_url_rewriter,cwd=dependency_path,)
@Registry.provide
def git_checkout_resolver(registry,git,git_resolver,ctx,dependency,dependency_path):
	if"checkout"in registry:
		checkout=registry.require("checkout")
	else:
		checkout=dependency.checkout
	return GitCheckoutResolver(git=git,resolver=git_resolver,ctx=ctx,dependency=dependency,checkout=checkout,cwd=dependency_path,)
@Registry.provide
def existing_checkout_resolver(registry,ctx,dependency,git_checkout_resolver,dependency_path):
	if"checkout"in registry:
		checkout=registry.require("checkout")
	else:
		checkout=dependency.checkout
	return ExistingCheckoutResolver(ctx=ctx,dependency=dependency,resolver=git_checkout_resolver,checkout=checkout,cwd=dependency_path,)
@Registry.provide
def git_semver_resolver(git,git_resolver,ctx,semver_selector,dependency,dependency_path):
	return GitSemverResolver(git=git,resolver=git_resolver,ctx=ctx,semver_selector=semver_selector,dependency=dependency,cwd=dependency_path,)
@Registry.provide
def existing_tag_resolver(ctx,dependency,semver_selector,tag_database,git_semver_resolver,dependency_path):
	return ExistingTagResolver(ctx=ctx,dependency=dependency,semver_selector=semver_selector,tag_database=tag_database,resolver=git_semver_resolver,cwd=dependency_path,)
@Registry.provide
def resolve_git_checkout(existing_checkout_resolver,dependency):
	dependency.resolver_action="git checkout"
	return existing_checkout_resolver
@Registry.provide
def resolve_git_user_checkout(registry,ctx,mandatory_options,dependency):
	checkout=mandatory_options.checkout(dependency=dependency)
	with registry.provide_temporary()as temporary:
		temporary.provide_value("checkout",checkout)
		resolver=registry.require("resolve_git_checkout")
		resolver=MandatoryResolver(resolver=resolver,msg="User checkout of '{}' failed.".format(checkout),dependency=dependency,)
	dependency.resolver_action="git user checkout"
	return resolver
@Registry.provide
def resolve_git_semver(registry,source,dependency):
	if"steinwurf"in source:
		resolver=registry.require("existing_tag_resolver")
	else:
		resolver=registry.require("git_semver_resolver")
	dependency.resolver_action="git semver"
	return resolver
@Registry.provide
def resolve_git(registry,ctx,options,dependency):
	checkout=options.checkout(dependency=dependency)
	if checkout:
		return registry.require("resolve_git_user_checkout")
	if"method"in registry:
		method=registry.require("method")
	else:
		method=dependency.method
	method_key="resolve_git_{}".format(method)
	git_resolver=registry.require(method_key)
	if options.fast_resolve():
		dependency.resolver_action="fast/"+dependency.resolver_action
		resolve_config_path=registry.require("resolve_config_path")
		fast_resolver=OnPassiveLoadPathResolver(dependency=dependency,resolve_config_path=resolve_config_path)
		fast_resolver=TryResolver(resolver=fast_resolver,ctx=ctx,dependency=dependency)
		return ListResolver(resolvers=[fast_resolver,git_resolver])
	else:
		return git_resolver
@Registry.cache
@Registry.provide
def resolve_from_lock_git(registry,lock_cache,dependency):
	checkout=lock_cache.checkout(dependency=dependency)
	with registry.provide_temporary()as temporary:
		temporary.provide_value("checkout",checkout)
		temporary.provide_value("method","checkout")
		resolver=registry.require("resolve_chain")
	resolver=CheckLockCacheResolver(resolver=resolver,lock_cache=lock_cache,dependency=dependency)
	return resolver
@Registry.cache
@Registry.provide
def resolve_http(options,registry,archive_extractor,url_download,dependency,source,ctx,dependency_path,):
	dependency.resolver_action="http"
	resolver=HttpResolver(url_download=url_download,dependency=dependency,source=source,cwd=dependency_path,)
	if dependency.extract:
		resolver=ArchiveResolver(archive_extractor=archive_extractor,resolver=resolver,cwd=dependency_path)
	if options.fast_resolve():
		dependency.resolver_action="fast/"+dependency.resolver_action
		resolve_config_path=registry.require("resolve_config_path")
		fast_resolver=OnPassiveLoadPathResolver(dependency=dependency,resolve_config_path=resolve_config_path)
		fast_resolver=TryResolver(resolver=fast_resolver,ctx=ctx,dependency=dependency)
		resolver=ListResolver(resolvers=[fast_resolver,resolver])
	return resolver
@Registry.provide
def resolve_from_lock_path(lock_cache,registry,dependency):
	with registry.provide_temporary()as temporary:
		temporary.provide_value("resolver","lock_path")
		resolver=registry.require("resolve_chain")
	resolver=CheckLockCacheResolver(resolver=resolver,lock_cache=lock_cache,dependency=dependency)
	return resolver
@Registry.provide
def resolve_lock_path(lock_cache,dependency):
	path=lock_cache.path(dependency=dependency)
	dependency.resolver_action="lock path"
	return PathResolver(dependency=dependency,path=path)
@Registry.provide
def help_chain(ctx,resolve_config_path,dependency):
	dependency.resolver_chain="Load"
	dependency.resolver_action="help"
	resolver=OnPassiveLoadPathResolver(dependency=dependency,resolve_config_path=resolve_config_path)
	resolver=TryResolver(resolver=resolver,ctx=ctx,dependency=dependency)
	return resolver
@Registry.provide
def load_chain(ctx,resolve_config_path,dependency):
	dependency.resolver_chain="Load"
	resolver=OnPassiveLoadPathResolver(dependency=dependency,resolve_config_path=resolve_config_path)
	resolver=TryResolver(resolver=resolver,ctx=ctx,dependency=dependency)
	resolver=CheckOptionalResolver(resolver=resolver,dependency=dependency)
	return resolver
@Registry.provide
def sources_resolver(ctx,registry,dependency):
	resolvers=[]
	for source in dependency.sources:
		with registry.provide_temporary()as temporary:
			temporary.provide_value("source",source)
			if"resolver"in registry:
				resolver=registry.require("resolver")
			else:
				resolver=dependency.resolver
			resolver_key="resolve_{}".format(resolver)
			resolver=registry.require(resolver_key)
			if"post_resolve"in dependency:
				temporary.provide_value("current_resolver",resolver)
				resolver=registry.require("post_resolve")
			resolver=TryResolver(resolver=resolver,ctx=ctx,dependency=dependency)
			resolvers.append(resolver)
	resolver=ListResolver(resolvers=resolvers)
	resolver=CheckOptionalResolver(resolver=resolver,dependency=dependency)
	return resolver
@Registry.provide
def resolve_chain(ctx,options,registry,dependency,resolve_config_path,symlinks_path):
	dependency.resolver_chain="Resolve"
	if options.path(dependency=dependency):
		resolver=registry.require("user_path_resolver")
	else:
		resolver=registry.require("sources_resolver")
	resolver=CreateSymlinkResolver(resolver=resolver,dependency=dependency,symlinks_path=symlinks_path,ctx=ctx)
	resolver=OnActiveStorePathResolver(resolver=resolver,dependency=dependency,resolve_config_path=resolve_config_path,)
	return resolver
@Registry.provide
def resolve_and_lock_chain(registry,dependency,project_path,lock_cache):
	resolver=registry.require("resolve_chain")
	lock_type=lock_cache.type()
	if lock_type=="versions":
		return StoreLockVersionResolver(resolver=resolver,lock_cache=lock_cache,dependency=dependency)
	elif lock_type=="paths":
		return StoreLockPathResolver(resolver=resolver,lock_cache=lock_cache,project_path=project_path,dependency=dependency,)
	else:
		raise WurfError("Unknown lock type {}".format(lock_type))
@Registry.provide
def resolve_from_lock_chain(registry,dependency,lock_cache):
	lock_type=lock_cache.type()
	if lock_type=="versions":
		resolver_key="resolve_from_lock_{}".format(dependency.resolver)
		resolver=registry.require(resolver_key)
	elif lock_type=="paths":
		resolver=registry.require("resolve_from_lock_path")
	else:
		raise WurfError("Unknown lock type {}".format(lock_type))
	return resolver
@Registry.provide
def dependency_resolver(registry,ctx,configuration,dependency):
	resolver_key="{}_chain".format(configuration.resolver_chain())
	resolver=registry.require(resolver_key)
	return ContextMsgResolver(resolver=resolver,ctx=ctx,dependency=dependency)
@Registry.cache_once
@Registry.provide
def configuration(options,args,project_path,waf_lock_file):
	return Configuration(options=options,args=args,project_path=project_path,waf_lock_file=waf_lock_file,)
@Registry.provide
def dependency_manager(registry):
	registry.purge_cache()
	ctx=registry.require("ctx")
	dependency_cache=registry.require("dependency_cache")
	options=registry.require("options")
	skip_internal=registry.require("skip_internal")
	return DependencyManager(registry=registry,dependency_cache=dependency_cache,ctx=ctx,options=options,skip_internal=skip_internal,)
@Registry.provide
def resolve_lock_action(lock_cache,project_path):
	def action():
		lock_path=os.path.join(project_path,Configuration.LOCK_FILE)
		lock_cache.write_to_file(lock_path)
	return action
@Registry.provide
def post_resolver_actions(registry,configuration):
	actions=[]
	if configuration.resolver_chain()==Configuration.RESOLVE_AND_LOCK:
		actions.append(registry.require("resolve_lock_action"))
	return actions
def resolve_registry(ctx,git_binary,default_resolve_path,resolve_config_path,default_symlinks_path,semver,archive_extractor,waf_utils,args,project_path,waf_lock_file,skip_internal,):
	registry=Registry()
	registry.provide_value("ctx",ctx)
	registry.provide_value("git_binary",git_binary)
	registry.provide_value("default_resolve_path",default_resolve_path)
	registry.provide_value("resolve_config_path",resolve_config_path)
	registry.provide_value("default_symlinks_path",default_symlinks_path)
	registry.provide_value("semver",semver)
	registry.provide_value("archive_extractor",archive_extractor)
	registry.provide_value("waf_utils",waf_utils)
	registry.provide_value("args",args)
	registry.provide_value("project_path",project_path)
	registry.provide_value("waf_lock_file",waf_lock_file)
	registry.provide_value("skip_internal",skip_internal)
	return registry
def options_registry(ctx,git_binary):
	registry=Registry()
	registry.provide_value("ctx",ctx)
	registry.provide_value("git_binary",git_binary)
	return registry
