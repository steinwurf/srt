#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import sys
import codecs
IS_PY2=sys.version_info[0]==2
def check_locale_python3():
	if IS_PY2:
		return
	try:
		import locale
		fs_enc=codecs.lookup(locale.getpreferredencoding()).name
	except LookupError:
		fs_enc="ascii"
	if fs_enc=="ascii":
		raise RuntimeError("We will abort further execution because Python 3 ""was configured to use ASCII as encoding for the ""environment. Consult e.g. http://click.pocoo.org/python3/""for mitigation steps.")
	else:
		return
