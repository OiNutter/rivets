import utils
import engines
import copy

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
  return trail.extensions - engines.engines.keys()

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

  #if block:
  #  name  = str(klass)
  #  klass = block

  _preprocessors[mime_type].append(klass)

def register_postprocessor(mime_type, klass, block = None):
  ''' Registers a new Postprocessor `klass` for `mime_type`.
  
        register_postprocessor 'text/css', rivets.charset_normalizer.CharsetNormalizer
    
      A block can be passed for to create a shorthand processor.
    
        register_postprocessor(lambda context, data: re.sub(...))
  '''

  #if block_given?
  #      name  = str(klass)
  #      klass = block

  _postprocessors[mime_type].append(klass)

def unregister_preprocessor(mime_type, klass):
  ''' Remove Preprocessor `klass` for `mime_type`.
    
        unregister_preprocessor('text/css', rivets.directive_processor.DirectiveProcessor)
  '''

  if isinstance(klass,string):
    for processor in _preprocessors:
      if processor.__name__ == klass:
        klass = processor
        break

  _preprocessors[mime_type].remove(klass)

def unregister_postprocessor(mime_type, klass):
  ''' Remove Postprocessor `klass` for `mime_type`

        unregister_postprocessor 'text/css', Sprockets::DirectiveProcessor
  '''

  if isinstance(klass,string):
    for processor in _postprocessors:
      if processor.__name__ == klass:
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
  #if block_given?
  #      name  = str(klass)
  #      klass = block

  _bundleprocessors[mime_type].append(klass)

def unregister_bundle_processor(mime_type, klass):
  ''' Remove Bundle Processor `klass` for `mime_type`.

        unregister_bundle_processor 'text/css', Sprockets::CharsetNormalizer
  '''
  
  if isinstance(klass,string):
    for processor in _postprocessors:
      if processor.__name__ == klass:
        klass = processor
        break

    _bundle_processors[mime_type].remove(klass)

def get_css_compressor():
  ''' Return CSS compressor or None if none is set '''
  compressor = None
  for processor in bundle_processors['text/css']:
    if processor == css_compressor:
      compressor = processor
    
def set_css_compressor(compressor=None):
  ''' Assign a compressor to run on `text/css` assets.

      The compressor object must respond to `compress` or `compile`.
  '''
  unregister_bundle_processor('text/css', css_compressor)
  if not compressor:
    return

  register_bundle_processor('text/css', compressor.compress);

def js_compressor(compressor=None):
  bundle_processors('application/javascript').detect { |klass|
        klass.respond_to?(:name) &&
          klass.name == 'Sprockets::Processor (js_compressor)'
      }
    end

    # Assign a compressor to run on `application/javascript` assets.
    #
    # The compressor object must respond to `compress` or `compile`.
    def js_compressor=(compressor)
      unregister_bundle_processor 'application/javascript', :js_compressor
      return unless compressor

      register_bundle_processor 'application/javascript', :js_compressor do |context, data|
        compressor.compress(data)
      end
    end

    private
      def add_engine_to_trail(ext, klass)
        @trail.append_extension(ext.to_s)

        if klass.respond_to?(:default_mime_type) && klass.default_mime_type
          if format_ext = extension_for_mime_type(klass.default_mime_type)
            @trail.alias_extension(ext.to_s, format_ext)
          end
        end
      end
  end
end
