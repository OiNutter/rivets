import re
import os

from ..extensions import get_extension
from ..utils import unique_list

class AssetAttributes:

	def __init__(self,environment,path):
		self.environment = environment
		self.path = path
		self.extensions = []

	def search_paths(self):
		paths = [self.path]

		path_without_extensions = self.path
		extensions = self.get_extensions()

		for ext in extensions:
			path_without_extensions = re.sub(ext,'',path_without_extensions)

		if '/' not in path_without_extensions:
			paths.append(os.path.join(path_without_extensions,'component.json'))

		if re.sub('|'.join([re.escape(ext) for ext in extensions]),'', os.path.basename(self.path)) != 'index':
			paths.append(os.path.join(path_without_extensions,"index%s"%''.join(extensions)))

		return paths

	def get_logical_path(self):
		root_path = ''

		for path in self.environment.paths():
			if path in self.path:
				root_path = path
				break

		path = re.sub("%s/"%root_path,'',self.path)
		path = os.path.relpath(self.path,root_path)
		for ext in self.get_engine_extensions():
			path = re.sub(ext,'',path)

		path = "%s%s" % (path,self.get_engine_format_extension()) if not self.get_format_extension() else path
		return path

	def get_asset_extension(self):
		return get_extension(self.path)

	def get_content_type(self):
		format_extension = self.get_format_extension()
		
		if format_extension:
			content_type = self.environment.mimetypes.get_mimetype(format_extension)
		else:
			content_type = self.get_engine_content_type()

		return content_type if content_type else 'application/octet-stream'

	def get_engine_extensions(self):
		exts = self.get_extensions()
		try:
			offset = exts.index(self.get_format_extension())
			exts = exts[offset+1:]
		except ValueError:
			exts = exts
		return [ext for ext in unique_list(exts) if self.environment.engines.get_engine(ext)]

	def get_engines(self):
		engine_extensions = self.get_engine_extensions()
		engines = []
		for ext in engine_extensions:
			engines.extend(self.environment.engines.get_engine(ext))
		return engines

	def get_engine_content_type(self):
		engines = list(self.get_engines())
		engines.reverse()

		for engine in engines:
			if getattr(engine,'default_mime_type',None):
				return engine.default_mime_type

	def get_engine_format_extension(self):
		content_type = self.get_engine_content_type()

		if content_type:
			return self.environment.mimetypes.get_extension_for_mimetype(content_type)

	def get_processors(self):
		content_type = self.get_content_type()
		ext = self.get_asset_extension()

		processors = []

		preprocessors = list(self.environment.processors.get_preprocessors(content_type))
		preprocessors.reverse()
		processors.extend(preprocessors)

		engines = self.environment.engines.get_engine(ext)
		engines.reverse()
		processors.extend(engines)

		postprocessors = list(self.environment.processors.get_postprocessors(content_type))
		postprocessors.reverse()
		processors.extend(postprocessors)

		return processors

	def get_extensions(self):
		basename = os.path.basename(self.path)
		extensions = self.extensions
		extensions.extend(re.findall(r"""\.[^.]+""",basename))
		return unique_list(extensions)

	def get_format_extension(self):
		extensions = list(self.get_extensions())
		extensions.reverse()

		for ext in extensions:
			if self.environment.mimetypes.get_mimetype(ext) and self.environment.engines.get_engine(ext) == []:
				return ext

		return None
