import regex as re
import os

from ..extensions import get_extension
from ..utils import unique_list

class AssetAttributes:

	def __init__(self,environment,path):
		self.environment = environment
		self.path = path
		self._extensions = []

	@property
	def search_paths(self):
		paths = [self.path]

		path_without_extensions = self.path
		extensions = self.extensions

		for ext in extensions:
			path_without_extensions = re.sub(ext,'',path_without_extensions)

		if '/' not in path_without_extensions:
			paths.append(os.path.join(path_without_extensions,'component.json'))

		if re.sub('|'.join([re.escape(ext) for ext in extensions]),'', os.path.basename(self.path)) != 'index':
			paths.append(os.path.join(path_without_extensions,"index%s"%''.join(extensions)))

		return paths

	@property
	def logical_path(self):
		root_path = ''

		for path in self.environment.paths:
			if path in self.path:
				root_path = path
				break

		path = re.sub("%s/"%root_path,'',self.path)
		path = os.path.relpath(self.path,root_path)
		for ext in self.engine_extensions:
			path = re.sub(ext,'',path)

		path = "%s%s" % (path,self.engine_format_extension) if not self.format_extension else path
		return path

	@property
	def asset_extension(self):
		return get_extension(self.path)

	@property
	def content_type(self):
		format_extension = self.format_extension
		
		if format_extension:
			content_type = self.environment.mimetypes.get_mimetype(format_extension)
		else:
			content_type = self.engine_content_type

		return content_type if content_type else 'application/octet-stream'

	@property
	def engine_extensions(self):
		exts = self.extensions
		try:
			offset = exts.index(self.format_extension)
			exts = exts[offset+1:]
		except ValueError:
			exts = exts
		return [ext for ext in unique_list(exts) if self.environment.engines.get_engine(ext)]

	@property
	def engines(self):
		engine_extensions = self.engine_extensions
		engines = []
		for ext in engine_extensions:
			engines.append(self.environment.engines.get_engine(ext))
		return engines

	@property
	def engine_content_type(self):
		engines = list(self.engines)
		engines.reverse()

		for engine in engines:
			if getattr(engine,'default_mime_type',None):
				return engine.default_mime_type

	@property
	def engine_format_extension(self):
		content_type = self.engine_content_type

		if content_type:
			return self.environment.mimetypes.get_extension_for_mimetype(content_type)

	@property
	def processors(self):
		content_type = self.content_type

		processors = []

		preprocessors = list(self.environment.processors.get_preprocessors(content_type))
		preprocessors.reverse()
		processors.extend(preprocessors)

		engines = self.engines
		engines.reverse()
		processors.extend(engines)

		postprocessors = list(self.environment.processors.get_postprocessors(content_type))
		postprocessors.reverse()
		processors.extend(postprocessors)

		return processors

	@property
	def extensions(self):
		basename = os.path.basename(self.path)
		extensions = self._extensions
		extensions.extend(re.findall(r"""\.[^.]+""",basename))
		return unique_list(extensions)

	@property
	def format_extension(self):
		extensions = list(self.extensions)
		extensions.reverse()

		for ext in extensions:
			if self.environment.mimetypes.get_mimetype(ext) and not self.environment.engines.get_engine(ext):
				return ext

		return None
