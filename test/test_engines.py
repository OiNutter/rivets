import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest
import regex as re
import copy

from rivets_test import RivetsTest
import rivets
from lean.template import Template

class AlertTemplate(Template):

	default_mime_type = 'application/javascript'

	def prepare(self):
		pass

	def evaluate(self,scope,local_vars,callback=None):
		return "alert(\"%s\");" % str(self.data)

class StringTemplate(Template):

	def prepare(self):
		pass

	def evaluate(self,scope,local_vars,callback=None):
		self.output = re.sub(r"""\{.*?\}""","moo",self.data)
		return self.output

class TestEngines(RivetsTest):
	
	ORIGINAL_ENGINES = copy.deepcopy(rivets.engines.engine_registry.engines)

	def setUp(self):
		rivets.engines.engine_registry.engines = copy.deepcopy(self.ORIGINAL_ENGINES)

	def tearDown(self):
		rivets.engines.engine_registry.engines = self.ORIGINAL_ENGINES

	def new_environment(self):
		env = rivets.Environment()
		env.append_path(self.fixture_path('engines'))
		return env

	def testRegisteringAGlobalEngine(self):
		''' Test registering a global engine '''
		registry = rivets.engines.engine_registry

		registry.register_engine('.alert',AlertTemplate)
		self.assertEqual(AlertTemplate,registry['alert'])
		self.assertEqual(AlertTemplate,registry['.alert'])

		env = self.new_environment()
		asset = env['hello.alert']

		self.assertEqual('alert("Hello world!\n");',str(asset))
		self.assertEqual('application/javascript',asset.content_type)

	def testOverridingAnEngineGlobally(self):
		''' Test overriding an engine globally '''

		env1 = self.new_environment()
		self.assertEqual(
				'console.log("Moo, {VERSION}");\n',
				str(env1['moo.js'])
			)

		registry = rivets.engines.engine_registry
		registry.register_engine('.str',StringTemplate)
		env2 = self.new_environment()
		self.assertEqual(
				'console.log("Moo, moo");\n',
				str(env2['moo.js'])
			)

	def testOverridingAnEngineInAnEnvironment(self):
		''' Test overriding an engine in an environment '''

		env1 = self.new_environment()
		env2 = self.new_environment()

		env1.register_engine('.str',StringTemplate)

		self.assertEqual(
				'console.log("Moo, moo");\n',
				str(env1['moo.js'])
			)
		self.assertEqual(
				'console.log("Moo, {VERSION}");\n',
				str(env2['moo.js'])
			)

if __name__ == '__main__':
    unittest.main()