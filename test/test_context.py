import sys
sys.path.insert(0,'../')
import unittest
import regex as re
import json

from rivets_test import RivetsTest
import rivets
from lean.template import Template

class TestContext(RivetsTest):

	def setUp(self):
		self.env = rivets.Environment('.')
		self.env.append_path(self.fixture_path('context'))

	def testContextEnvironmentIsIndexed(self):
		''' Test context environment is indexed '''

		instances = str(self.env['environment.js']).split('\n')
		assert re.search("Index",instances[0])
		self.assertEqual(instances[0],instances[1])

	def testSourceFilePropertiesAreExposedInContext(self):
		''' Test source file properties are exposed in context '''
		
		properties = str(self.env['properties.js']).rstrip('\n').rstrip(';')
		expected = {
				'pathname':self.fixture_path('context/properties.js.mako'),
				'root_path':self.fixture_path('context'),
				"logical_path":'properties',
				'content_type':"application/javascript"
			}

		assert expected == json.loads(properties)

	def testSourceFilePropertiesAreExposedInContextWhenPathContainsPeriods(self):
		''' Test source file properties are exposed in context when path contains periods'''

		properties = str(self.env['properties.with.periods.js']).rstrip('\n').rstrip(';')
		expected = {
				'pathname':self.fixture_path('context/properties.with.periods.js.mako'),
				'root_path':self.fixture_path('context'),
				"logical_path":'properties.with.periods',
				'content_type':"application/javascript"
			}

		assert expected == json.loads(properties)

	def testExtendContext(self):
		''' Test extend context '''

		def datauri(self,path):
			import base64
			s = base64.b64encode(open(path,'rb').read())
			return '\n'.join(s[pos:pos+60] for pos in xrange(0, len(s), 60))



		self.env.context_class.datauri = datauri
		
		self.assertEqual(
				".pow {  background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAEsCAMAAADNS4U5AAAAGXRFWHRTb2Z0",
				''.join(str(self.env["helpers.css"]).splitlines()[0:2])
			)

		self.assertEqual(58239,self.env['helpers.css'].length)

class YamlProcessor(Template):

	def initialize_engine(self):
		global yaml
		import yaml

	def prepare(self):
		self.manifest = yaml.load(self.data)

	def evaluate(self, context, local_vars=None,block=None):
		for logical_path in self.manifest['require']:
			context.require_asset(logical_path)

		return ""

class DataURIProcessor(Template):

	def initialize_engine(self):
		global base64
		import base64

	def prepare(self):
		pass

	def evaluate(self,context,local_vars=None,block=None):
		self.output = self.data
		def replace_url(match):
			path = context.resolve(match.group(1))
			context.depend_on(path)
			s = base64.b64encode(open(path,'rb').read())
			data = '\n'.join(s[pos:pos+60] for pos in xrange(0, len(s), 60))
			return "url(data:image/png;base64,%s)"%data

		self.output = re.sub(r'''url\("(.+?)"\)''',replace_url,self.output)
		return self.output

class TestCustomProcessor(RivetsTest):

	def setUp(self):
		self.env = rivets.Environment()
		self.env.append_path(self.fixture_path('context'))

	def testCustomProcessorUsingContextRequire(self):
		''' Test custom processor using Context#require '''
		self.env.register_engine('.yml',YamlProcessor)
		self.assertEqual(
				"var Foo = {};\nvar Bar = {};\n",
				str(self.env['application.js'])
			)

	def testCustomProcessorUsingContextResolveAndContextDependOn(self):
		''' Test custom processor using Context#resolve and Context#depend_on '''
		self.env.register_engine('embed',DataURIProcessor)

		self.assertEqual(
				".pow {  background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAEsCAMAAADNS4U5AAAAGXRFWHRTb2Z0",
				''.join(str(self.env["sprite.css"]).splitlines()[0:2])	
			)
		
		self.assertEqual(58239,self.env['sprite.css'].length)

	def testBlockCustomProcessor(self):
		''' Test block custom processor '''
		import base64

		def process_asset(self,context,data):
			self.output = self.data
			def replace_url(match):
				path = context.resolve(match.group(1))
				context.depend_on(path)
				s = base64.b64encode(open(path,'rb').read())
				data = '\n'.join(s[pos:pos+60] for pos in xrange(0, len(s), 60))
				return "url(data:image/png;base64,%s)"%data

			self.output = re.sub(r'''url\("(.+?)"\)''',replace_url,self.output)
			return self.output

		self.env.register_preprocessor('text/css','data_uris',process_asset)

		self.assertEqual(
				".pow {  background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZoAAAEsCAMAAADNS4U5AAAAGXRFWHRTb2Z0",
					''.join(str(self.env["sprite.css.embed"]).splitlines()[0:2])
			)

		self.assertEqual(58239,self.env['sprite.css.embed'].length)

	def testResolveWithContentType(self):
		''' Test resolve with content type '''
		print str(self.env['resolve_content_type.js']).strip()
		self.assertEqual(
				',\n'.join([
					self.fixture_path("context/foo.js"),
					self.fixture_path("context/foo.js"),
					self.fixture_path("context/foo.js"),
					"foo.js is 'application/javascript', not 'text/css';"
				]),
				str(self.env['resolve_content_type.js']).strip()
			)

if __name__ == '__main__':
    unittest.main()