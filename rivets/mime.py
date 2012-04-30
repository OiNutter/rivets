import mimetypes
import utils

mime_types = mimetypes.types_map

def mime_types(ext = None):
	''' Returns a `Hash` of registered mime types registered on the
		environment and those part of `Rack::Mime`.

		If an `ext` is given, it will lookup the mime type for that extension.      
	'''
	if not ext:
		return mimetypes.types_map.update(mime_types)
	else:
		ext = utils.normalize_extension(ext)
		return mime_types[ext]

	def registered_mime_types():
		''' Returns a `Hash` of explicitly registered mime types. '''
		return mime_types.copy()

	def extension_for_mime_type(type):
		return mime_types.key(type)

	def register_mime_type(mime_type, ext):
		''' Register a new mime type. '''
		ext = utils.normalize_extension(ext)
		mime_types[ext] = mime_type
