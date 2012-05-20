# Define some basic Sprockets error classes
class Error(StandardError):
	pass

class ArgumentError(Error):
	pass

class CircularDependencyError(Error):
	pass

class ContentTypeMismatch(Error):
	pass
  
class EncodingError(Error):
	pass

class FileNotFound(Error):
	pass

class FileOutsidePaths(Error):
	pass

class UnserializeError(Error):
	pass

class EngineError(Error):
	@property
	def sprockets_annotation(self):
		return self._sprockets_annotation

	def message(self):
		"\\n".join([super, self.sprockets_annotation])