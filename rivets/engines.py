from directive_processor import DirectiveProcessor
import re
import os
import codecs

def get_engine_for_file(file,env):
	file_name,file_ext = os.path.splitext(file)

	if(file_ext == '.js'):
		return JS(env)
	elif(file_ext=='.css'):
		return CSS(env)
	elif(file_ext=='.css.scss'):
		return SCSS(env)
	elif(file_ext=='.js.coffee'):
		return Coffee(env)
	else:
		return Engine(env)

#####################
# Base Engine Class #
#####################
class Engine:

	_supported_extensions = []

	def _preprocess(self,content):
		return content

	def _postprocess(self,content):
		return content

	def process(self,content):
		return content

#####################
# Javascript Engine #
#####################
class JS(Engine):

	def __init__(self,env):
		self._supported_extensions.append('js')
		self._env = env

	def process(self,content):
		directives = DirectiveProcessor.find_directives(content)
		content = self._preprocess(content)
		if directives:
			for directive in directives:
				if directive and not directive[2] in self._env._included_files:
					found_includes = self._env._trail.find(re.sub(r' ','',directive[2]))

					if found_includes:
						engine = get_engine_for_file(found_includes[0],self._env)
						included_content = codecs.open(found_includes[0],'r',self._env._default_encoding).read()
						included_content = engine.process(included_content)
						print '### Include ###'
						print included_content
						content = engine.replace_directive(content,included_content,directive)
						print '### Processed Content ###'
						print content

		return self._postprocess(content)

	def replace_directive(self,content,include,directive):
		pattern = re.compile(r"//= " + directive[0])
		return pattern.sub(include,content)

##############
# CSS Engine #
##############
class CSS(Engine):

	def __init__(self,env):
		self._supported_extensions.append('css')
		self._env = env

#######################
# CoffeeScript Engine #
#######################
class Coffee(Engine):

	def __init__(self,env):
		self._supported_extensions.append('js')
		self._supported_extensions.append('coffee')
		self._env = env

###############
# SASS Engine #
###############
class SCSS(Engine):

	def __init__(self,env):
		self._supported_extensions.append('css')
		self._supported_extensions.append('scss')
		self._env = env