import re
import os

from ..extensions import get_extension

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

		if re.sub('|'.join([re.escape(ext) for ext in extensions]),'', os.path.basename(self.path)) != 'index':
			paths.append(os.path.join(path_without_extensions,"index%s"%''.join(extensions)))

		return paths

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
			offset = self.get_extensions.index(self.get_format_extension())
			exts = exts[offset+1:]
		except ValueError:
			exts = exts

		return [ext for ext in exts if self.environment.engines.get_engine(ext)]

	def get_engines(self):
		engine_extensions = self.get_engine_extensions()

		return [self.environment.engines.get_engine(ext) for ext in engine_extensions]


	def get_engine_content_type(self):
		engines = list(self.get_engines)
		engines.reverse()

		for engine in engines:
			if getattr(engine,'default_mime_type',None):
				return engine.default_mime_type

	def get_processors(self):
		content_type = self.get_content_type()
		ext = self.get_asset_extension()

		processors = []

		preprocessors = list(self.environment.processors.get_preprocessors(content_type))
		preprocessors.reverse()
		processors.extend(preprocessors)

		engine = self.environment.engines.get_engine(ext)
		if engine:
			processors.append(engine)

		postprocessors = list(self.environment.processors.get_postprocessors(content_type))
		postprocessors.reverse()
		processors.extend(postprocessors)

		return processors

	def get_extensions(self):
		basename = os.path.basename(self.path)
		extensions = self.extensions
		extensions.extend(re.findall(r"""\.[^.]+""",basename))
		return extensions

	def get_format_extension(self):
		extensions = list(self.get_extensions())
		extensions.reverse()

		for ext in extensions:
			if self.environment.mimetypes.get_mimetype(ext) and not self.environment.engines.get_engine(ext):
				return ext

		return None
