from shift.template import Template
import re

class CharsetNormalizer(Template):
	''' Some browsers have issues with stylesheets that contain multiple
		`@charset` definitions. The issue surfaces while using Sass since
  		it inserts a `@charset` at the top of each file. Then Sprockets
  		concatenates them together.
  		
  		The `CharsetNormalizer` processor strips out multiple `@charset`
 		definitions.

		The current implementation is naive. It picks the first `@charset`
  		it sees and strips the others. This works for most people because
  		the other definitions are usually `UTF-8`. A more sophisticated
  		approach would be to re-encode stylesheets with mixed encodings.
  		
  		This behavior can be disabled with:
  			environment.unregister_bundle_processor('text/css', rivets.charset_normalizer.CharsetNormalizer)
  	'''

  	def prepare():
  		pass

	def evaluate(self,context, locals, block=None):
		charset = None

		# Find and strip out any `@charset` definitions
		results = re.search(r'^@charset "([^"]+)";$',self.data)

		for result in results:
			if not charset:
				charset = result

			self.data = re.sub(result,'',self.data)

		if charset:
			# If there was a charset, move it to the top
			return "@charset \"%s\";%s" % (charset,self.data)
		else:
			return self.data
