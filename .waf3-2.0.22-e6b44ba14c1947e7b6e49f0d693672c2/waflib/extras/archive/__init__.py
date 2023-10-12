#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import os
import sys
import tarfile
import zipfile
from.compat import IS_PY2,is_string
class ArchiveException(Exception):
	pass
class UnrecognizedArchiveFormat(ArchiveException):
	pass
class UnsafeArchive(ArchiveException):
	pass
def extract(path,to_path='',ext='',**kwargs):
	Archive(path,ext=ext).extract(to_path,**kwargs)
class Archive(object):
	def __init__(self,file,ext=''):
		self._archive=self._archive_cls(file,ext=ext)(file)
	@staticmethod
	def _archive_cls(file,ext=''):
		cls=None
		filename=None
		if is_string(file):
			filename=file
		else:
			try:
				filename=file.name
			except AttributeError:
				raise UnrecognizedArchiveFormat("File object not a recognized archive format.")
		lookup_filename=filename+ext
		base,tail_ext=os.path.splitext(lookup_filename.lower())
		cls=extension_map.get(tail_ext)
		if not cls:
			base,ext=os.path.splitext(base)
			cls=extension_map.get(ext)
		if not cls:
			raise UnrecognizedArchiveFormat("Path not a recognized archive format: %s"%filename)
		return cls
	def extract(self,*args,**kwargs):
		self._archive.extract(*args,**kwargs)
	def list(self):
		self._archive.list()
class BaseArchive(object):
	def __del__(self):
		if hasattr(self,"_archive"):
			self._archive.close()
	def list(self):
		raise NotImplementedError()
	def filenames(self):
		raise NotImplementedError()
	def _extract(self,to_path):
		self._archive.extractall(to_path)
	def extract(self,to_path='',method='safe'):
		if method=='safe':
			self.check_files(to_path)
		elif method=='insecure':
			pass
		else:
			raise ValueError("Invalid method option")
		self._extract(to_path)
	def check_files(self,to_path=None):
		if to_path:
			target_path=os.path.normpath(os.path.realpath(to_path))
		else:
			target_path=os.getcwd()
		for filename in self.filenames():
			extract_path=os.path.join(target_path,filename)
			extract_path=os.path.normpath(os.path.realpath(extract_path))
			if not extract_path.startswith(target_path):
				raise UnsafeArchive("Archive member destination is outside the target"" directory.  member: %s"%filename)
class TarArchive(BaseArchive):
	def __init__(self,file):
		if is_string(file):
			self._archive=tarfile.open(name=file)
		else:
			self._archive=tarfile.open(fileobj=file)
	def list(self,*args,**kwargs):
		self._archive.list(*args,**kwargs)
	def filenames(self):
		return self._archive.getnames()
class ZipArchive(BaseArchive):
	def __init__(self,file):
		self._archive=zipfile.ZipFile(file)
	def list(self,*args,**kwargs):
		self._archive.printdir(*args,**kwargs)
	def filenames(self):
		return self._archive.namelist()
	def _extract_file(self,info,to_path):
		out_path=self._archive.extract(info.filename,path=to_path)
		permissions=info.external_attr>>16
		if permissions:
			os.chmod(out_path,permissions)
	def _extract(self,to_path):
		for info in self._archive.infolist():
			self._extract_file(info=info,to_path=to_path)
extension_map={'.docx':ZipArchive,'.egg':ZipArchive,'.jar':ZipArchive,'.odg':ZipArchive,'.odp':ZipArchive,'.ods':ZipArchive,'.odt':ZipArchive,'.pptx':ZipArchive,'.tar':TarArchive,'.tar.bz2':TarArchive,'.tar.gz':TarArchive,'.tgz':TarArchive,'.tz2':TarArchive,'.xlsx':ZipArchive,'.zip':ZipArchive,}
