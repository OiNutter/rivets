import utils

engines = {}

def engines(ext = None):
	''' Returns a `Hash` of `Engine`s registered on the `Environment`.
    	If an `ext` argument is supplied, the `Engine` associated with
    	that extension will be returned.
    	
    	environment.engines()
    	# => {".coffee" => CoffeeScriptTemplate, ".sass" => SassTemplate, ...}
    	
    	environment.engines('.coffee')
    	# => CoffeeScriptTemplate
    '''
	if ext:
		ext = utils.normalize_extension(ext)
		return engines.engines[ext]
	else:
		return engines.engines.copy()

def engine_extensions():
	''' Returns a `List` of engine extension `String`s.
    		
    	environment.engine_extensions()
    	# => ['.coffee', '.sass', ...]
	'''
	return engines.engines.keys()

def register_engine(ext,klass):
	''' Registers a new Engine `klass` for `ext`. If the `ext` already
   		has an engine registered, it will be overridden.

    	environment.register_engine '.coffee', CoffeeScriptTemplate
   	'''

	ext = utils.normalize_extension(ext)
	engines.engines[ext] = klass