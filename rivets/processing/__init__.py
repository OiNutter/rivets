from registry import ProcessorRegistry

from directive_processor import DirectiveProcessor
from safety_colons import SafetyColons

from uglipyjs_compressor import UglipyJSCompressor
from rjsmin_compressor import RJSMinCompressor
from cssmin_compressor import CSSMinCompressor
from slimit_compressor import SlimitCompressor
from slimmer_compressors import SlimmerJSCompressor, SlimmerCSSCompressor

ProcessorRegistry.register_preprocessor('application/javascript',DirectiveProcessor)
ProcessorRegistry.register_preprocessor('text/css',DirectiveProcessor)

ProcessorRegistry.register_postprocessor('application/javascript',SafetyColons)

ProcessorRegistry.register_compressor('application/javascript','uglify',UglipyJSCompressor)
ProcessorRegistry.register_compressor('application/javascript','uglipy',UglipyJSCompressor)
ProcessorRegistry.register_compressor('application/javascript','uglipyjs',UglipyJSCompressor)
ProcessorRegistry.register_compressor('application/javascript','uglifier',UglipyJSCompressor)

ProcessorRegistry.register_compressor('application/javascript','rjsmin',RJSMinCompressor)

ProcessorRegistry.register_compressor('application/javascript','slimit',SlimitCompressor)

ProcessorRegistry.register_compressor('application/javascript','slimmer',SlimmerJSCompressor)
ProcessorRegistry.register_compressor('application/javascript','slimmerjs',SlimmerJSCompressor)

ProcessorRegistry.register_compressor('text/css','cssmin',CSSMinCompressor)

ProcessorRegistry.register_compressor('text/css','slimmer',SlimmerCSSCompressor)
ProcessorRegistry.register_compressor('text/css','slimmercss',SlimmerCSSCompressor)