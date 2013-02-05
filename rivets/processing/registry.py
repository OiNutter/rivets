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

	def register_preprocessor(self,mimetype,processor,callback=None):
		self.register_processor('pre',mimetype,processor,callback)

	def register_postprocessor(self,mimetype,processor,callback=None):
		self.register_processor('post',mimetype,processor,callback)

	def register_bundleprocessor(self,mimetype,processor,callback=None):
		self.register_processor('bundle',mimetype,processor,callback)

	def register_processor(self,position,mimetype,processor,callback=None):

		if callback:
			name = str(processor)
			processor = type(name,(Processor,),{"processor":callback})

		if not self.processors[position].has_key(mimetype):
			self.processors[position][mimetype] = []

		self.processors[position][mimetype].append(processor)

	def unregister_preprocessor(self,mimetype,processor):
		return self.unregister_processor('pre',mimetype,processor)

	def unregister_postprocessor(self,mimetype,processor):
		return self.unregister_processor('post',mimetype,processor)

	def unregister_bundleprocessor(self,mimetype,processor):
		return self.unregister_processor('bundle',mimetype,processor)

	def unregister_processor(self,position,mimetype,processor):

		if self.processors[position].has_key(mimetype):
			if not isinstance(processor,str):
				self.processors[position][mimetype].remove(processor)
			else:
				for klass in self.processors[position][mimetype]:
					if klass.__name__ == processor:
						self.processors[position][mimetype].remove(klass)


	def get_preprocessors(self,mimetype):
		return self.get_processors('pre',mimetype)

	def get_postprocessors(self,mimetype):
		return self.get_processors('post',mimetype)

	def get_bundleprocessors(self,mimetype):
		return self.get_processors('bundle',mimetype)

	def get_processors(self,position,mimetype):
		if self.processors[position].has_key(mimetype):
			return self.processors[position][mimetype]
		else:
			return []

	def register_compressor(self,mimetype,name,processor):
		
		if not self.compressors.has_key(mimetype):
			self.compressors[mimetype] = {}

		self.compressors[mimetype][name] = processor

	def unregister_compressor(self,mimetype,name):
		if self.compressors.has_key(mimetype):
			del self.compressors[mimetype][name]

	def get_compressors(self,mimetype):
		return self.compressors[mimetype] if self.compressors.has_key(mimetype) else []

	def get_js_compressor(self):
		return self.js_compressor

	def set_js_compressor(self,processor):
		self.unregister_bundleprocessor('application/javascript',self.js_compressor)

		self.js_compressor = processor

		self.register_bundleprocessor('application/javascript',processor)

	def get_css_compressor(self):
		return self.css_compressor

	def set_css_compressor(self,processor):
		self.unregister_bundleprocessor('text/css',self.css_compressor)

		self.css_compressor = processor

		self.register_bundleprocessor('text/css',processor)