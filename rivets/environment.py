import io
from crawl import Crawl

from directive_processor import DirectiveProcessor
from extensions import get_extension
from includes import Include

class Environment:

	files = []
	default_encoding = 'utf8'
	
	def __init__(self,root="."):
		self.search_path = Crawl(root)

	def add_path(self,path):
		self.search_path.append_path(path)

	def add_paths(self,paths):
		for path in paths:
			self.search_path.append_path(path)

	def compile(self,path):
		
		output = Include(path,self)

		return output.process()












