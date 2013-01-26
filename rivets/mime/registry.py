import mimetypes

class MimeTypeRegistry:

	mimetypes = {}

	def register_mimetype(self,extension,mimetype):
		self.mimetypes[extension] = mimetype.lower()

	def get_mimetype(self,extension):
	
		if self.mimetypes.has_key(extension):
			return self.mimetypes[extension]
		else:

			return mimetypes.types_map[extension] if mimetypes.types_map.has_key(extension) else None

	def get_extension_for_mimetype(self,mime):

		for ext,mimetype in self.mimetypes.iteritems():
			if mimetype.lower() == mime.lower():
				return ext