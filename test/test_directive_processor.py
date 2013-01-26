import sys
sys.path.insert(0,'../')
if sys.version_info[:2] == (2,6):
	import unittest2 as unittest
else:
	import unittest

from rivets_test import RivetsTest
import rivets

class TestDirectiveProcessor(RivetsTest):

	def directive_parser(self,fixture_name):
		return rivets.processing.DirectiveProcessor(self.fixture_path("directives/%s"%fixture_name))

	def directive_fixture(self,name):
		return self.fixture("directives/%s"%name)

	def directives(self,offset=0):
		return [
				(3+offset,'require','a'),
				(4+offset,'require','b'),
				(6+offset,'require','c')
			]

	def testParsingDoubleSlashComments(self):
		''' Test parsing double-slash comments '''
		parser = self.directive_parser("double_slash")

		self.assertEqual(
			"// Header\n//\n\n\n//\n\n(function() {\n})();\n",
			parser.processed_source
		)

		self.assertEqual(self.directives(),parser.directives)

	def testParsingHashComments(self):
		''' Test parsing hash comments '''
		parser = self.directive_parser("hash")

		self.assertEqual(
			"# Header\n#\n\n\n#\n\n(->)()\n",
			parser.processed_source
		)

		self.assertEqual(self.directives(),parser.directives)

	def testParsingSlashStarComments(self):
		''' Test parsing slash-star comments '''
		parser = self.directive_parser("slash_star")

		self.assertEqual(
			"/* Header\n *\n\n\n *\n\n */\n\n(function() {\n})();\n",
			parser.processed_source
		)

		self.assertEqual(self.directives(),parser.directives)

	def testParsingSingleLineSlashStarComments(self):
		''' Test parsing single line slash-star comments '''
		parser = self.directive_parser("slash_star_single")

		self.assertEqual(
			"\n(function() {\n})();\n",
			parser.processed_source
		)

		self.assertEqual([(1, "require", "a")],parser.directives)

	def testParsingTripleHashComments(self):
		''' Test parsing triple-hash comments '''
		parser = self.directive_parser("triple_hash")

		self.assertEqual(
			"###\nHeader\n\n\n\n\n\n###\n\n(->)()\n",
			parser.processed_source
		)

		self.assertEqual(self.directives(1),parser.directives)

	def testHeaderCommentWithoutDirectivesIsUnmodified(self):
		''' Test header comment without directives is unmodified '''
		parser = self.directive_parser("comment_without_directives")

		self.assertEqual(
				"/*\n * Comment\n */\n\n(function() {\n})();\n",
				parser.processed_source
			)
		self.assertEqual([],parser.directives)


	def testDirectivesInCommentAfterHeaderAreNotParsed(self):
		''' Test directives in comment after header are not parsed '''
		parser = self.directive_parser("directives_after_header")

		self.assertEqual(
				"/*\n * Header\n\n */\n\n\n\n\n\n\n/* Not a directive */\n\n(function() {\n})();\n\n/*= require e */\n",
				parser.processed_source
			)

		self.assertEqual(
				[
					(3, "require", "a"),
	        		(6, "require", "b"),
	        		(7, "require", "c"),
	        		(9, "require", "d")
				],
				parser.directives
			)

	def testHeadersMustOccurAtTheBeginningOfTheFile(self):
		''' Test headers must occur at the beginning of the file '''
		parser = self.directive_parser("code_before_comment")

		self.assertEqual("",parser.processed_header)
		self.assertEqual([],parser.directives)

	def testNoHeader(self):
		''' Test no header '''
		parser = self.directive_parser("no_header")

		self.assertEqual(
				self.directive_fixture("no_header"),
				parser.processed_source
			)
		self.assertEqual([],parser.directives)

	def testDirectiveWordSplitting(self):
		''' Test directive word splitting '''

		parser = self.directive_parser("directive_word_splitting")

		self.assertEqual(
				[
					(1, "require"),
	        		(2, "require", "two"),
	        		(3, "require", "two", "three"),
	        		(4, "require", "two three"),
	        		(6, "require", "seven")
	        	],
	        	parser.directives
			)

	def testSpaceBetweenEqualsandDirectiveWord(self):
		''' Test space between = and directive word '''
		parser = self.directive_parser("space_between_directive_word")

		self.assertEqual("var foo;\n",parser.processed_source)
		self.assertEqual([(1,"require","foo")],parser.directives)

	def testDocumentationHeaders(self):
		''' Test documentation headers '''
		parser = self.directive_parser("documentation")

		self.assertEqual(
				"\n//\n// = Foo\n//\n// == Examples\n//\n// Foo.bar()\n// => \"baz\"\nvar Foo;\n",
				parser.processed_source
			)
		self.assertEqual([(1,"require","project")],parser.directives)

class CustomDirectiveProcessor(rivets.processing.DirectiveProcessor):

	def process_require_glob_directive(self,glob_path):
		import glob
		import os
		for filename in sorted(glob.glob("%s/%s" %(os.path.dirname(self._file),glob_path))):
			self.context.require_asset(filename)

class TestCustomDirectiveProcessor(RivetsTest):

	def setUp(self):
		self.env = rivets.Environment()
		self.env.append_path(self.fixture_path('context'))

	def testCustomProcessorUsingContextResolveAndContextDepend(self):
		''' Test custom processor using Context#rivets_resolve and Context#rivets_depend '''

		self.env.unregister_preprocessor('application/javascript',rivets.processing.DirectiveProcessor)
		self.env.register_preprocessor('application/javascript',CustomDirectiveProcessor)

		self.assertEqual("var Foo = {};\n",str(self.env["require_glob.js"]))


if __name__ == '__main__':
    unittest.main()