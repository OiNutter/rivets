## -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest
import cherrypy
from cherrypy.test import helper
import os
import datetime, time
import regex as re

import rivets
from rivets_test import RivetsTest

class TestServer(RivetsTest,helper.CPWebCase):

	def setUp(self):
		self.env = TestServer.get_env()

	def get_header(self,key):
		key = key.lower()
		for k,v in self.headers:
			if k.lower() == key:
				return v

		return None

	@staticmethod
	def get_env():
		env = rivets.Environment()
		env.append_path(TestServer._fixture_path("server/app/javascripts"))
		env.append_path(TestServer._fixture_path("server/vendor/javascripts"))
		env.append_path(TestServer._fixture_path("server/vendor/stylesheets"))	
		return env

	@staticmethod
	def _fixture_path(path):
		if path == TestServer.FIXTURE_ROOT:
			return path
		else:
			return os.path.join(TestServer.FIXTURE_ROOT,path)

	@staticmethod
	def setup_server():

		env = TestServer.get_env()

		try:
			import routes
		except ImportError:
			raise unittest.SkipTest('Install routes to test Server')

		d = cherrypy.dispatch.RoutesDispatcher()

		d.connect('assets','/assets/:path',controller = env, action='run')
		d.connect('cached','/cached/javascripts/:path',controller = env.index, action='run')

		conf = {
				'/':{
					'request.dispatch':d
				}
			}

		cherrypy.tree.mount(root=None,config=conf)

	def testServeSingleSourceFile(self):
		''' Test serve single source file '''

		self.getPage("/assets/foo.js")		
		self.assertBody('var foo;\n')

	def testServeSingleSourceFileBody(self):
		''' Test serve single source file '''

		self.getPage("/assets/foo.js?body=1")		
		self.assertStatus('200 OK')
		self.assertBody('var foo;\n')
		self.assertHeader('Content-Length','9')

	def testServeSingleSourceFileFromIndexedEnvironment(self):
		''' Test serve single source file from indexed environment '''

		self.getPage("/cached/javascripts/foo.js")		
		self.assertBody('var foo;\n')

	def testServeSourceWithDependencies(self):
		''' Test serve source with dependencies '''

		self.getPage("/assets/application.js")		
		self.assertBody('var foo;\n\n(function() {\n  application.boot();\n})();\n')

	def testServeSourceFileBodyThatHasDependencies(self):
		''' Test serve source file body that has dependencies '''

		self.getPage("/assets/application.js?body=true")		
		self.assertStatus('200 OK')
		self.assertBody("\n(function() {\n  application.boot();\n})();\n")
		self.assertHeader('Content-Length','43')

	def testServeSourceWithContentTypeHeaders(self):
		''' Test serve source with content type headers '''

		self.getPage("/assets/application.js")		
		self.assertHeader('Content-Type','application/javascript')

	def testServeSouceWithEtagHeaders(self):
		''' Test serve source with ETag headers '''

		digest = self.env['application.js'].digest
		self.getPage("/assets/application.js")
		self.assertHeader('ETag','"%s"'%digest)

	def testUpdatedFileUpdatesTheLastModifiedHeader(self):
		''' Test updated file updates the last modified header '''

		now = time.mktime(datetime.datetime.now().timetuple())
		path = TestServer._fixture_path('server/app/javascripts/foo.js')

		def do_test():

			os.utime(path,(now,now))

			self.getPage('/assets/application.js')
			time_before_modifying = self.get_header('Last-Modified')

			self.getPage('/assets/application.js')
			time_after_modifying = self.get_header('Last-Modified')

			self.assertEqual(time_before_modifying,time_after_modifying)

			f = open(path,'w')
			f.write('(change)')
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(path,(new_time,new_time))

			self.getPage('/assets/application.js')
			time_after_modifying = self.get_header('Last-Modified')

			self.assertNotEqual(time_before_modifying,time_after_modifying)

		self.sandbox(path,callback=do_test)

	def testFileUpdatesDoNotUpdateTheLastModifiedHeaderInIndexedEnvironment(self):
		''' Test file updates do not update last modified header for indexed environments '''

		now = time.mktime(datetime.datetime.now().timetuple())
		path = TestServer._fixture_path('server/app/javascripts/foo.js')

		def do_test():

			os.utime(path,(now,now))

			self.getPage('/cached/javascripts/application.js')
			time_before_modifiying = self.get_header('Last-Modified')

			self.getPage('/cached/javascripts/application.js')
			time_after_modifiying = self.get_header('Last-Modified')

			self.assertEqual(time_before_modifiying,time_after_modifiying)

			f = open(path,'w')
			f.write('(change)')
			f.close()
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(path,(new_time,new_time))

			self.getPage('/cached/javascripts/application.js')
			time_after_modifiying = self.get_header('Last-Modified')

			self.assertEqual(time_before_modifiying,time_after_modifiying)

		self.sandbox(path,callback=do_test)

	def testNotModifiedPartialResponseWhenEtagsMatch(self):
		''' Test not modified partial response when etags match '''

		self.getPage('/assets/application.js?body=1')
		self.assertStatus('200 OK')
		etag = self.get_header('ETag')

		self.getPage('/assets/application.js?body=1',headers=[('HTTP_IF_NONE_MATCH',etag)])

		self.assertStatus('304 Not Modified')
		self.assertHeader('Content-Type',None)
		self.assertNoHeader('Content-Length')

	def testIfSourcesDidntChangeTheServerShouldntRebundle(self):
		''' Test if the sources didn't change the server shouldn't rebundle '''

		self.getPage('/assets/application.js')
		asset_before = self.env['application.js']
		assert asset_before

		self.getPage('/assets/application.js')
		asset_after = self.env['application.js']
		assert asset_after

		assert asset_before.equals(asset_after)

	def testFingerprintDigestSetsExpirationToTheFuture(self):
		''' Test fingerprint digest sets expiration to the future '''

		self.getPage('/assets/application.js')
		digest = re.findall(r'''"(.+)"''',self.get_header('ETag'))[0]

		self.getPage('/assets/application-%s.js'%digest)
		self.assertStatus('200 OK')
		self.assertRegexpMatches(self.get_header('Cache-Control'),re.compile(r"""max-age"""))

	def testMissingSource(self):
		''' Test missing source '''

		self.getPage('/assets/none.js')
		self.assertStatus('404 Not Found')
		self.assertHeader('X-Cascade','pass')

	def testReThrowJSExceptionsInTheBrowser(self):
		''' Test re-throw JS exceptions in the browser '''

		self.getPage('/assets/missing_require.js')
		self.assertStatus('200 OK')
		self.assertBody("throw Error(\"FileNotFound: Couldn't find file 'notfound'\\n  (in %s:1)\")"%TestServer._fixture_path('server/vendor/javascripts/missing_require.js'))

	def testDisplayCSSExceptionsInTheBrowser(self):
		''' Test display css exceptions in the browser '''

		self.getPage('/assets/missing_require.css')
		self.assertStatus('200 OK')
		self.assertRegexpMatches(self.body,re.compile(r"""content: ".*?FileNotFound""",re.S))

	def testServeEncodedUTF8Pathname(self):
		''' Test server encoded utf-8 pathname '''

		self.getPage("/assets/%E6%97%A5%E6%9C%AC%E8%AA%9E.js")
		self.assertBody("var japanese = \"日本語\";\n")

	def testAddNewSourceToTree(self):
		''' Test add new source to tree '''

		filename = TestServer._fixture_path('server/app/javascripts/baz.js')

		def do_test():
			self.getPage('/assets/tree.js')
			self.assertBody("var foo;\n\n(function() {\n  application.boot();\n})();\nvar bar;\nvar japanese = \"日本語\";\n")

			with open(filename,'w') as f:
				f.write('var baz;')

			path = TestServer._fixture_path('server/app/javascripts')
			new_time = time.mktime((datetime.datetime.now()+datetime.timedelta(seconds=1)).timetuple())
			os.utime(path,(new_time,new_time))

			self.getPage('/assets/tree.js')
			self.assertBody("var foo;\n\n(function() {\n  application.boot();\n})();\nvar bar;\nvar baz;\nvar japanese = \"日本語\";\n")

		self.sandbox(filename,callback=do_test)

	def testServingStaticAssets(self):
		''' Test serving static assets '''

		self.getPage('/assets/hello.txt')
		self.assertStatus('200 OK')
		self.assertHeader('Content-Type','text/plain;charset=utf-8')
		self.assertBody(open(TestServer._fixture_path('server/app/javascripts/hello.txt')).read())

if __name__ == '__main__':
    unittest.main()