import os
import copy
import crawl

class Paths(object):

	search_path = crawl.Crawl(os.path.realpath(os.path.relpath('..',__file__)))

	@property
	def root(self):
		return copy.deepcopy(self.search_path.root)

	@property
	def paths(self):
		return copy.deepcopy(self.search_path.paths)

	def prepend_path(self,*paths):
			self.prepend_paths(*paths)

	def prepend_paths(self,*paths):
		self.search_paths.append_paths(*paths)

	def append_path(self,*paths):
		self.append_paths(*paths)

	def append_paths(self,*paths):
		self.search_path.append_paths(*paths)

	def clear_paths(self):
		for path in copy.deepcopy(self.search_path.paths):
			self.search_path.remove_path(path)

path_registry = Paths()