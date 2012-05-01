import engines
import copy
from processor import Processor
import mime
import rivets

''' `Processing` is an internal mixin whose public methods are exposed on
    the `Environment` and `Index` classes.
'''

_preprocessors = {}
_postprocessors = {}
_bundleprocessors = {}
    
def format_extensions():
  ''' Returns a `List` of format extension `String`s.

      format_extensions
      # => ['.js', '.css']
  '''
  return rivets.trail.extensions - engines.engines.keys()

def preprocessors(mime_type = None):
  ''' Returns an `Array` of `Processor` classes. If a `mime_type`
      argument is supplied, the processors registered under that
      extension will be returned.

      Preprocessors are ran before Postprocessors and Engine
      processors.

      All `Processor`s must follow the `Tilt::Template` interface. It is
      recommended to subclass `Tilt::Template`.
  '''
  if mime_type:
    return copy.copy(_preprocessors[mime_type])
  else:
    return copy.deepcopy(_preprocessors)

def postprocessors(mime_type = None):
  ''' Returns an `Array` of `Processor` classes. If a `mime_type`
      argument is supplied, the processors registered under that
      extension will be returned.

      Postprocessors are ran after Preprocessors and Engine processors.

      All `Processor`s must follow the `Tilt::Template` interface. It is
      recommended to subclass `Tilt::Template`.
  '''
  if mime_type:
    return copy.copy(_postprocessors[mime_type])
  else:
    return copy.deepcopy(_postprocessors)

def register_preprocessor(mime_type, klass, block=None):
  ''' Registers a new Preprocessor `klass` for `mime_type`.
    
        register_preprocessor 'text/css', rivets.directive_processor.DirectiveProcessor
      
      A block can be passed for to create a shorthand processor.
        
        register_preprocessor(lambda context, data: re.sub(...))
  '''

  if block:
    name  = str(klass)
    klass = Processor(name,block)

  _preprocessors[mime_type].append(klass)

def register_postprocessor(mime_type, klass, block = None):
  ''' Registers a new Postprocessor `klass` for `mime_type`.
  
        register_postprocessor 'text/css', rivets.charset_normalizer.CharsetNormalizer
    
      A block can be passed for to create a shorthand processor.
    
        register_postprocessor(lambda context, data: re.sub(...))
  '''

  if block:
    name  = str(klass)
    klass = Processor(name,block)

  _postprocessors[mime_type].append(klass)

def unregister_preprocessor(mime_type, klass):
  ''' Remove Preprocessor `klass` for `mime_type`.
    
        unregister_preprocessor('text/css', rivets.directive_processor.DirectiveProcessor)
  '''

  if isinstance(klass,'string'):
    for processor in _preprocessors:
      if processor.__name__ =='rivets.processor.Processor (%s)' % klass:
        klass = processor
        break

  _preprocessors[mime_type].remove(klass)

def unregister_postprocessor(mime_type, klass):
  ''' Remove Postprocessor `klass` for `mime_type`

        unregister_postprocessor 'text/css', Sprockets::DirectiveProcessor
  '''

  if isinstance(klass,'string'):
    for processor in _postprocessors:
      if processor.__name__ == 'rivets.processor.Processor (%s)' % klass:
        klass = processor
        break

  _postprocessors[mime_type].remove(klass)

def bundle_processors(mime_type = None):
  ''' Returns an `Array` of `Processor` classes. If a `mime_type`
      argument is supplied, the processors registered under that
      extension will be returned.
      
      Bundle Processors are ran on concatenated assets rather than
      individual files.
    
      All `Processor`s must follow the `shift.template.Template` interface. It is
      recommended to subclass `shift.template.Template`.
  '''
  if mime_type:
        copy.copy(_bundleprocessors[mime_type])
  else:
        copy.deepcopy(_bundleprocessors)

def register_bundle_processor(mime_type, klass, block=None):
  ''' Registers a new Bundle Processor `klass` for `mime_type`.
        register_bundle_processor  'text/css', Sprockets::CharsetNormalizer
    
      A block can be passed for to create a shorthand processor.
      
        register_bundle_processor(lambda context, data: re.sub(...))
  '''
  if block:
    name  = str(klass)
    klass = Processor(name,block)

  _bundleprocessors[mime_type].append(klass)

def unregister_bundle_processor(mime_type, klass):
  ''' Remove Bundle Processor `klass` for `mime_type`.

        unregister_bundle_processor 'text/css', Sprockets::CharsetNormalizer
  '''
  
  if isinstance(klass,'string'):
    for processor in _postprocessors:
      if processor.__name__ == 'rivets.processor.Processor (%s)' % klass:
        klass = processor
        break

    _bundleprocessors[mime_type].remove(klass)

def get_css_compressor():
  ''' Return CSS compressor or None if none is set '''
  compressor = None
  for processor in bundle_processors['text/css']:
    if processor.__name__ == 'rivets.processor.Processor (CSSCompressor)':
      compressor = processor
  return compressor
    
def set_css_compressor(compressor=None):
  ''' Assign a compressor to run on `text/css` assets.

      The compressor object must respond to `compress` or `compile`.
  '''
  unregister_bundle_processor('text/css', 'CSSCompressor')
  if not compressor:
    return

  klass = Processor('CSSCompressor',lambda context,data:compressor.compress(data))

  register_bundle_processor('text/css', klass)

def get_js_compressor():
  ''' Return JS compressor or None if none is set '''
  compressor = None
  for processor in bundle_processors['application/javascript']:
    if processor.__name__ == 'rivets.processor.Processor (JSCompressor)':
      compressor = processor
  return compressor
 
def set_js_compressor(compressor=None):
  ''' Assign a compressor to run on `application/javascript` assets.

      The compressor object must respond to `compress` or `compile`.
  '''
  unregister_bundle_processor('application/javascript','JSCompressor')
  if not compressor:
    return

  klass = Processor('JSCompressor',lambda context,data:compressor.compress(data))

  register_bundle_processor('application/javascript', klass)

  def add_engine_to_trail(ext, klass):
    rivets.trail.append_extension(str(ext))

    if hasattr(klass,'default_mime_type') and callable(klass,'default_mime_type') and klass.default_mime_type():
      format_ext = mime.extension_for_mime_type(klass.default_mime_type)
      if format_ext:
        return rivets.trail.alias_extension(str(ext), format_ext)
