from crawl import Crawl

from extensions import get_extension
from includes import Include
from processors import ProcessorRegistry

class Environment:

	files = []
	default_encoding = 'utf8'
	root = ""

	output_extensions = {
		".coffee":".js",
		".scss":".css"
	}
	
	def __init__(self,root="."):
		self.root = root
		self.search_path = Crawl(root)

	def add_path(self,path):
		self.search_path.append_path(path)

	def add_paths(self,paths):
		for path in paths:
			self.search_path.append_path(path)

	def compile(self,path):
		
		include = Include(path,self)
		output = include.process()
		ext = get_extension(path)
		ext = self.output_extensions[ext] if self.output_extensions.has_key(ext) else ext

		#run post processors
		post_processors = ProcessorRegistry.get_postprocessors(ext)

		for processor in post_processors:
			output = processor(block=lambda x: output.encode(self.default_encoding)).render()

		minifier = ProcessorRegistry.get_minifier(ext)

		if minifier:
			output = minifier(block=lambda x: output.encode(self.default_encoding)).render()

		return output












