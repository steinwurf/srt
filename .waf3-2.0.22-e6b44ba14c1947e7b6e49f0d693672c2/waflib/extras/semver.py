#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

from __future__ import print_function
import argparse
import collections
from functools import wraps
import re
import sys
__version__='2.9.0'
__author__='Kostiantyn Rybnikov'
__author_email__='k-bx@k-bx.com'
__maintainer__='Sebastien Celles'
__maintainer_email__="s.celles@gmail.com"
_REGEX=re.compile(r"""
        ^
        (?P<major>(?:0|[1-9][0-9]*))
        \.
        (?P<minor>(?:0|[1-9][0-9]*))
        \.
        (?P<patch>(?:0|[1-9][0-9]*))
        (\-(?P<prerelease>
            (?:0|[1-9A-Za-z-][0-9A-Za-z-]*)
            (\.(?:0|[1-9A-Za-z-][0-9A-Za-z-]*))*
        ))?
        (\+(?P<build>
            [0-9A-Za-z-]+
            (\.[0-9A-Za-z-]+)*
        ))?
        $
        """,re.VERBOSE)
_LAST_NUMBER=re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
SEMVER_SPEC_VERSION="2.0.0"
if not hasattr(__builtins__,'cmp'):
	def cmp(a,b):
		return(a>b)-(a<b)
def parse(version):
	match=_REGEX.match(version)
	if match is None:
		raise ValueError('%s is not valid SemVer string'%version)
	version_parts=match.groupdict()
	version_parts['major']=int(version_parts['major'])
	version_parts['minor']=int(version_parts['minor'])
	version_parts['patch']=int(version_parts['patch'])
	return version_parts
def comparator(operator):
	@wraps(operator)
	def wrapper(self,other):
		comparable_types=(VersionInfo,dict,tuple)
		if not isinstance(other,comparable_types):
			raise TypeError("other type %r must be in %r"%(type(other),comparable_types))
		return operator(self,other)
	return wrapper
class VersionInfo(object):
	__slots__=('_major','_minor','_patch','_prerelease','_build')
	def __init__(self,major,minor=0,patch=0,prerelease=None,build=None):
		self._major=int(major)
		self._minor=int(minor)
		self._patch=int(patch)
		self._prerelease=None if prerelease is None else str(prerelease)
		self._build=None if build is None else str(build)
	@property
	def major(self):
		return self._major
	@major.setter
	def major(self,value):
		raise AttributeError("attribute 'major' is readonly")
	@property
	def minor(self):
		return self._minor
	@minor.setter
	def minor(self,value):
		raise AttributeError("attribute 'minor' is readonly")
	@property
	def patch(self):
		return self._patch
	@patch.setter
	def patch(self,value):
		raise AttributeError("attribute 'patch' is readonly")
	@property
	def prerelease(self):
		return self._prerelease
	@prerelease.setter
	def prerelease(self,value):
		raise AttributeError("attribute 'prerelease' is readonly")
	@property
	def build(self):
		return self._build
	@build.setter
	def build(self,value):
		raise AttributeError("attribute 'build' is readonly")
	def _astuple(self):
		return(self.major,self.minor,self.patch,self.prerelease,self.build)
	def _asdict(self):
		return collections.OrderedDict((("major",self.major),("minor",self.minor),("patch",self.patch),("prerelease",self.prerelease),("build",self.build)))
	def __iter__(self):
		for v in self._astuple():
			yield v
	def bump_major(self):
		return parse_version_info(bump_major(str(self)))
	def bump_minor(self):
		return parse_version_info(bump_minor(str(self)))
	def bump_patch(self):
		return parse_version_info(bump_patch(str(self)))
	def bump_prerelease(self,token='rc'):
		return parse_version_info(bump_prerelease(str(self),token))
	def bump_build(self,token='build'):
		return parse_version_info(bump_build(str(self),token))
	@comparator
	def __eq__(self,other):
		return _compare_by_keys(self._asdict(),_to_dict(other))==0
	@comparator
	def __ne__(self,other):
		return _compare_by_keys(self._asdict(),_to_dict(other))!=0
	@comparator
	def __lt__(self,other):
		return _compare_by_keys(self._asdict(),_to_dict(other))<0
	@comparator
	def __le__(self,other):
		return _compare_by_keys(self._asdict(),_to_dict(other))<=0
	@comparator
	def __gt__(self,other):
		return _compare_by_keys(self._asdict(),_to_dict(other))>0
	@comparator
	def __ge__(self,other):
		return _compare_by_keys(self._asdict(),_to_dict(other))>=0
	def __repr__(self):
		s=", ".join("%s=%r"%(key,val)for key,val in self._asdict().items())
		return"%s(%s)"%(type(self).__name__,s)
	def __str__(self):
		return format_version(*(self._astuple()))
	def __hash__(self):
		return hash(self._astuple())
	@staticmethod
	def parse(version):
		return parse_version_info(version)
	def replace(self,**parts):
		version=self._asdict()
		version.update(parts)
		try:
			return VersionInfo(**version)
		except TypeError:
			unknownkeys=set(parts)-set(self._asdict())
			error=("replace() got %d unexpected keyword ""argument(s): %s"%(len(unknownkeys),", ".join(unknownkeys)))
			raise TypeError(error)
def _to_dict(obj):
	if isinstance(obj,VersionInfo):
		return obj._asdict()
	elif isinstance(obj,tuple):
		return VersionInfo(*obj)._asdict()
	return obj
def parse_version_info(version):
	parts=parse(version)
	version_info=VersionInfo(parts['major'],parts['minor'],parts['patch'],parts['prerelease'],parts['build'])
	return version_info
def _nat_cmp(a,b):
	def convert(text):
		return int(text)if re.match('^[0-9]+$',text)else text
	def split_key(key):
		return[convert(c)for c in key.split('.')]
	def cmp_prerelease_tag(a,b):
		if isinstance(a,int)and isinstance(b,int):
			return cmp(a,b)
		elif isinstance(a,int):
			return-1
		elif isinstance(b,int):
			return 1
		else:
			return cmp(a,b)
	a,b=a or'',b or''
	a_parts,b_parts=split_key(a),split_key(b)
	for sub_a,sub_b in zip(a_parts,b_parts):
		cmp_result=cmp_prerelease_tag(sub_a,sub_b)
		if cmp_result!=0:
			return cmp_result
	else:
		return cmp(len(a),len(b))
def _compare_by_keys(d1,d2):
	for key in['major','minor','patch']:
		v=cmp(d1.get(key),d2.get(key))
		if v:
			return v
	rc1,rc2=d1.get('prerelease'),d2.get('prerelease')
	rccmp=_nat_cmp(rc1,rc2)
	if not rccmp:
		return 0
	if not rc1:
		return 1
	elif not rc2:
		return-1
	return rccmp
def compare(ver1,ver2):
	v1,v2=parse(ver1),parse(ver2)
	return _compare_by_keys(v1,v2)
def match(version,match_expr):
	prefix=match_expr[:2]
	if prefix in('>=','<=','==','!='):
		match_version=match_expr[2:]
	elif prefix and prefix[0]in('>','<'):
		prefix=prefix[0]
		match_version=match_expr[1:]
	else:
		raise ValueError("match_expr parameter should be in format <op><ver>, ""where <op> is one of ""['<', '>', '==', '<=', '>=', '!=']. ""You provided: %r"%match_expr)
	possibilities_dict={'>':(1,),'<':(-1,),'==':(0,),'!=':(-1,1),'>=':(0,1),'<=':(-1,0)}
	possibilities=possibilities_dict[prefix]
	cmp_res=compare(version,match_version)
	return cmp_res in possibilities
def max_ver(ver1,ver2):
	cmp_res=compare(ver1,ver2)
	if cmp_res==0 or cmp_res==1:
		return ver1
	else:
		return ver2
def min_ver(ver1,ver2):
	cmp_res=compare(ver1,ver2)
	if cmp_res==0 or cmp_res==-1:
		return ver1
	else:
		return ver2
def format_version(major,minor,patch,prerelease=None,build=None):
	version="%d.%d.%d"%(major,minor,patch)
	if prerelease is not None:
		version=version+"-%s"%prerelease
	if build is not None:
		version=version+"+%s"%build
	return version
def _increment_string(string):
	match=_LAST_NUMBER.search(string)
	if match:
		next_=str(int(match.group(1))+1)
		start,end=match.span(1)
		string=string[:max(end-len(next_),start)]+next_+string[end:]
	return string
def bump_major(version):
	verinfo=parse(version)
	return format_version(verinfo['major']+1,0,0)
def bump_minor(version):
	verinfo=parse(version)
	return format_version(verinfo['major'],verinfo['minor']+1,0)
def bump_patch(version):
	verinfo=parse(version)
	return format_version(verinfo['major'],verinfo['minor'],verinfo['patch']+1)
def bump_prerelease(version,token='rc'):
	verinfo=parse(version)
	verinfo['prerelease']=_increment_string(verinfo['prerelease']or(token or'rc')+'.0')
	return format_version(verinfo['major'],verinfo['minor'],verinfo['patch'],verinfo['prerelease'])
def bump_build(version,token='build'):
	verinfo=parse(version)
	verinfo['build']=_increment_string(verinfo['build']or(token or'build')+'.0')
	return format_version(verinfo['major'],verinfo['minor'],verinfo['patch'],verinfo['prerelease'],verinfo['build'])
def finalize_version(version):
	verinfo=parse(version)
	return format_version(verinfo['major'],verinfo['minor'],verinfo['patch'])
def createparser():
	parser=argparse.ArgumentParser(prog=__package__,description=__doc__)
	s=parser.add_subparsers()
	parser_compare=s.add_parser("compare",help="Compare two versions")
	parser_compare.set_defaults(which="compare")
	parser_compare.add_argument("version1",help="First version")
	parser_compare.add_argument("version2",help="Second version")
	parser_bump=s.add_parser("bump",help="Bumps a version")
	parser_bump.set_defaults(which="bump")
	sb=parser_bump.add_subparsers(title="Bump commands",dest="bump")
	for p in(sb.add_parser("major",help="Bump the major part of the version"),sb.add_parser("minor",help="Bump the minor part of the version"),sb.add_parser("patch",help="Bump the patch part of the version"),sb.add_parser("prerelease",help="Bump the prerelease part of the version"),sb.add_parser("build",help="Bump the build part of the version")):
		p.add_argument("version",help="Version to raise")
	return parser
def process(args):
	if args.which=="bump":
		maptable={'major':'bump_major','minor':'bump_minor','patch':'bump_patch','prerelease':'bump_prerelease','build':'bump_build',}
		ver=parse_version_info(args.version)
		func=getattr(ver,maptable[args.bump])
		return str(func())
	elif args.which=="compare":
		return str(compare(args.version1,args.version2))
def main(cliargs=None):
	try:
		parser=createparser()
		args=parser.parse_args(args=cliargs)
		result=process(args)
		print(result)
		return 0
	except(ValueError,TypeError)as err:
		print("ERROR",err,file=sys.stderr)
		return 2
def replace(version,**parts):
	version=parse_version_info(version)
	return str(version.replace(**parts))
