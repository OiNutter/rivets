from registry import ProcessorRegistry

from directive_processor import DirectiveProcessor
from safety_colons import SafetyColons
from charset_normalizer import CharsetNormalizer

from uglipyjs_compressor import UglipyJSCompressor
from rjsmin_compressor import RJSMinCompressor
from cssmin_compressor import CSSMinCompressor
from slimit_compressor import SlimitCompressor
from slimmer_compressors import SlimmerJSCompressor, SlimmerCSSCompressor

processor_registry = ProcessorRegistry()

processor_registry.register_preprocessor('application/javascript',DirectiveProcessor)
processor_registry.register_preprocessor('text/css',DirectiveProcessor)

processor_registry.register_postprocessor('application/javascript',SafetyColons)

processor_registry.register_bundleprocessor('text/css',CharsetNormalizer)

processor_registry.register_compressor('application/javascript','uglify',UglipyJSCompressor)
processor_registry.register_compressor('application/javascript','uglipy',UglipyJSCompressor)
processor_registry.register_compressor('application/javascript','uglipyjs',UglipyJSCompressor)
processor_registry.register_compressor('application/javascript','uglifier',UglipyJSCompressor)

processor_registry.register_compressor('application/javascript','rjsmin',RJSMinCompressor)

processor_registry.register_compressor('application/javascript','slimit',SlimitCompressor)

processor_registry.register_compressor('application/javascript','slimmer',SlimmerJSCompressor)
processor_registry.register_compressor('application/javascript','slimmerjs',SlimmerJSCompressor)

processor_registry.register_compressor('text/css','cssmin',CSSMinCompressor)

processor_registry.register_compressor('text/css','slimmer',SlimmerCSSCompressor)
processor_registry.register_compressor('text/css','slimmercss',SlimmerCSSCompressor)