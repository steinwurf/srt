#! /usr/bin/env python
# encoding: utf-8
# WARNING! Do not edit! https://waf.io/book/index.html#_obtaining_the_waf_file

class GitUrlRewriter(object):
	git_protocols={"https://":"https://{host}/{path}.git","http://":"http://{host}/{path}.git","git@":"git@{host}:{path}.git","git://":"git://{host}/{path}.git","ssh://git@":"git@{host}:{path}.git",}
	def __init__(self,parser,rewrite_protocol):
		self.parser=parser
		if rewrite_protocol in GitUrlRewriter.git_protocols:
			self.format_url=GitUrlRewriter.git_protocols[rewrite_protocol]
		else:
			self.format_url=rewrite_protocol
	def rewrite_url(self,url):
		u=self.parser.parse(url)
		if u.protocol is None:
			return self.format_url.format(host=u.host,path=u.path)
		else:
			return url
