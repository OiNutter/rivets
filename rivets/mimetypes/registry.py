class MimeTypeRegistry:

	mimetypes = {}

	@staticmethod
	def register_mimetype(extension,mimetype):

		MimeTypeRegistry.mimetypes[extension] = mimetype.lower()

	@staticmethod
	def get_mimetype(extension):
	
		if MimeTypeRegistry.mimetypes.has_key(extension):
			return MimeTypeRegistry.mimetypes[extension]
		else:
			return None

	@staticmethod
	def get_extension_for_mimetype(mimetype):

		for ext,mimetype in MimeTypeRegistry.mimetypes.iteritems():
			if mimetype.lower() == mimetype.lower():
				return ext