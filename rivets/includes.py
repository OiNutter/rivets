from extensions import get_extension
from engines import EngineRegistry
from directive_processor import DirectiveProcessor
from safety_colons import SafetyColons

class Include:
	
	directives = []

	processed_directives = ""

	VALID_EXTENSIONS = {
		".js":[".js",".js.coffee"],
		".coffee":[".js",".js.coffee"],
		".css":[".css",".css.scss"],
		".scss":[".css",".css.scss"]
	}

	def __init__(self,path,environment):
		
		self.environment = environment
		self.path = path

		self.ext = get_extension(path)

		self.environment.search_path.append_extensions(self.VALID_EXTENSIONS[self.ext])

		self.engine = EngineRegistry.get_engine(self.ext)(self.path,{'default_encoding':self.environment.default_encoding})

	def process(self):
		
		self.directives = DirectiveProcessor.find_directives(self.engine.data)

		self.engine.data = DirectiveProcessor.strip_directives(self.engine.data)

		for directive in self.directives:

			if not directive in self.environment.files:
				files = self.environment.search_path.find(directive[2])

				if files:
					self.environment.files.append(directive[2])


					processed = Include(files[0],self.environment).process()
					
					
					self.processed_directives += processed + "\n"

		output = self.engine.render()
		#print output
		output = self.processed_directives + output

		return SafetyColons(block=lambda x: output).render()
