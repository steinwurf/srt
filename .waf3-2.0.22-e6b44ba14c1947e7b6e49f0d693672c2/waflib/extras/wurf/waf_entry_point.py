#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

import sys
from waflib import Errors
from.import waf_resolve_context
from.import waf_options_context
from.import waf_configuration_context
from.import waf_build_context
from.import waf_install_context
from.import waf_standalone_context
from.import waf_conf
assert waf_resolve_context
assert waf_options_context
assert waf_configuration_context
assert waf_build_context
assert waf_install_context
assert waf_standalone_context
assert waf_conf
def _check_minimum_python_version(major,minor):
	if sys.version_info[:2]<(major,minor):
		raise Errors.ConfigurationError("Python version not supported: {0}, ""required minimum version: {1}.{2}".format(sys.version_info[:3],major,minor))
_check_minimum_python_version(3,6)
