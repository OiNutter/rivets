from processor import Processor

class ProcessorRegistry:

	# list of processors to be run before or after engine processors
	processors = {
		"pre":{},
		"post":{},
		"bundle":{}
	}

	# special list of post processors to be run as the last processors
	compressors = {}
	js_compressor=None
	css_compressor=None

	@staticmethod
	def register_preprocessor(mimetype,processor,callback=None):
		ProcessorRegistry.register_processor('pre',mimetype,processor,callback)

	@staticmethod
	def register_postprocessor(mimetype,processor,callback=None):
		ProcessorRegistry.register_processor('post',mimetype,processor,callback)

	@staticmethod
	def register_bundleprocessor(mimetype,processor,callback=None):
		ProcessorRegistry.register_processor('bundle',mimetype,processor,callback)

	@staticmethod
	def register_processor(position,mimetype,processor,callback=None):

		if callback:
			name = str(processor)
			processor = type(name,(Processor,),{"processor":callback})

		if not ProcessorRegistry.processors[position].has_key(mimetype):
			ProcessorRegistry.processors[position][mimetype] = []

		ProcessorRegistry.processors[position][mimetype].append(processor)

	@staticmethod
	def unregister_preprocessors(mimetype,processor):
		return ProcessorRegistry.unregister_processors('pre',mimetype,processor)

	@staticmethod
	def unregister_postprocessors(mimetype,processor):
		return ProcessorRegistry.unregister_processors('post',mimetype,processor)

	@staticmethod
	def unregister_bundleprocessors(mimetype,processor):
		return ProcessorRegistry.unregister_processors('bundle',mimetype,processor)

	@staticmethod
	def unregister_processors(position,mimetype,processor):
		if ProcessorRegistry.processors[position].has_key(mimetype):
			ProcessorRegistry.processors[position][mimetype].remove(processor)

	@staticmethod
	def get_preprocessors(mimetype):
		return ProcessorRegistry.get_processors('pre',mimetype)

	@staticmethod
	def get_postprocessors(mimetype):
		return ProcessorRegistry.get_processors('post',mimetype)

	@staticmethod
	def get_bundleprocessors(mimetype):
		return ProcessorRegistry.get_processors('bundle',mimetype)

	@staticmethod
	def get_processors(position,mimetype):
		if ProcessorRegistry.processors[position].has_key(mimetype):
			return ProcessorRegistry.processors[position][mimetype]
		else:
			return []



	@staticmethod
	def register_compressor(mimetype,name,processor):
		
		if not ProcessorRegistry.compressors.has_key(mimetype):
			ProcessorRegistry.compressors[mimetype] = {}

		ProcessorRegistry.compressors[mimetype][name] = processor

	@staticmethod
	def get_compressors(mimetype):
		return ProcessorRegistry.compressors[mimetype] if ProcessorRegistry.compressors.has_key(mimetype) else []

	@staticmethod
	def get_js_compressor():
		return ProcessorRegistry.js_compressor

	@staticmethod
	def set_js_compressor(processor):
		ProcessorRegistry.unregister_bundleprocessor('application/javascript',ProcessorRegistry.js_compressor)

		ProcessorRegistry.js_compressor = processor

		ProcessorRegistry.register_bundleprocessor('application/javascript',processor)