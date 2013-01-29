class EngineError(Exception):
	pass

class MimeTypeError(Exception):
	pass

class ContentTypeMismatch(Exception):
	pass

class UnserializeError(Exception):
	pass

class FileNotFound(Exception):
	pass

class FileOutsidePaths(Exception):
	pass

class ArgumentError(Exception):
	pass

class CircularDependencyError(Exception):
	pass

class EncodingError(Exception):
	pass