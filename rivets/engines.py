from directive_processor import DirectiveProcessor
import re
import os
import io
import coffeescript

def get_engine_for_file(file,env):
	file_name,file_ext = os.path.splitext(file)

	if(file_ext == '.js'):
		print '### JS ###'
		return JS(file,env)
	elif(file_ext=='.css'):
		print '### CSS ###'
		return CSS(file,env)
	elif(file_ext=='.scss'):
		print '### SCSS ###'
		return SCSS(file,env)
	elif(file_ext=='.coffee'):
		print '### COFFEE ###'
		return Coffee(file,env)
	else:
		print file_ext
		return Engine(file,env)

#####################
# Base Engine Class #
#####################
class Engine(object):

	_supported_extensions = []
	_includes = {}

	def __init__(self,file,env):
		self._env = env
		self._file = io.open(file,'r',encoding = self._env._default_encoding)
		self._includes = {}

	def _preprocess(self):
		self._processed_content = ""

	def _postprocess(self):
		return None

	def process(self):
		self._preprocess()
		directives = DirectiveProcessor.find_directives(self._file)
		self._includes = {}
		

		i = 1
		for line in self._file:
			
			if directives and directives.has_key(i) and not directives[i][2] in self._env._included_files:
				print 'matched line'
				found_includes = self._env._trail.find(re.sub(r' ','',directives[i][2]))

				if found_includes:
					engine = get_engine_for_file(found_includes[0],self._env)
					self._processed_content = self._processed_content + engine.process()
				else:
					self._processed_content = self._processed_content + line
			else:
					self._processed_content = self._processed_content + line

			i = i +1

		self._postprocess()

		return self._processed_content

#####################
# Javascript Engine #
#####################
class JS(Engine):

	def __init__(self,file,env):
		self._supported_extensions.extend(['.js','.js.coffee'])
		super(JS,self).__init__(file,env)

##############
# CSS Engine #
##############
class CSS(Engine):

	def __init__(self,file,env):
		self._supported_extensions.extend(['.css','.css.scss'])
		super(CSS,self).__init__(file,env)

#######################
# CoffeeScript Engine #
#######################
class Coffee(Engine):

	def __init__(self,file,env):
		self._supported_extensions.append('js')
		self._supported_extensions.append('coffee')
		super(Coffee,self).__init__(file,env)

	def _preprocess(self):
		# replace comments with block comments so they're preserved
		self._replace_comments()
		content = self._file.read()
		self._file = io.TextIOBase().write(coffeescript.compile(content))

	def _replace_comments(self):
		comment_pattern = re.compile(r"(\\\#.*(?:\\n))")
		content = self._file.read()
		matches = comment_pattern.findall(content)
		print '### Comments ###'
		print matches
		for match in matches:
			content.sub(match[0],'### ' + match[1] + ' ###')
		self._file = io.TextIOBase().write(content)

###############
# SASS Engine #
###############
class SCSS(Engine):

	def __init__(self,env):
		self._supported_extensions.append('css')
		self._supported_extensions.append('scss')
		self._env = env