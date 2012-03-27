import engines
import crawl
import codecs
import os
from directive_processor import DirectiveProcessor

class Environment:

	_valid_exts = ['.js','.css','.css.scss','.js.coffee']
	_default_encoding = 'UTF-8'

	def __init__(self, root="."):
		self._trail = crawl.Trail(root)
		self._trail.append_extensions(self._valid_exts)
		self._included_files = []

	def add_path(self,path):
		self._trail.append_path(path)

	def add_paths(self,paths):
		self._trail.append_paths(paths)

	def compile(self,target):
		found_files = self._trail.find(target)

		if not found_files:
			return False

		processed_content = content = codecs.open(found_files[0],'r').read()
		engine = engines.get_engine_for_file(found_files[0],self)	
		processed_content = engine.process(content)

		return processed_content
