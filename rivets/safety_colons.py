from shift.template import Template
import re

class SafetyColons(Template):
	''' For JS developers who are colonfobic, concatenating JS files using
		the module pattern usually leads to syntax errors.
  		
  		The `SafetyColons` processor will insert missing semicolons to the
 		end of the file.
	
		This behavior can be disabled with:

  			environment.unregister_postprocessor('application/javascript', rivets.safety_colons.SafetyColons)
  	'''
  	
	def prepare(self):
		pass

   	def evaluate(self,context, locals, block=None):
   		''' If the file is blank or ends in a semicolon, leave it as is '''
   		if re.search(r"\A\s*\Z",self.data,re.M) or re.search(r";\s*\Z",re.M):
   			return self.data
		else:
			# Otherwise, append a semicolon and newline
			return "%s;\n" % self.data
