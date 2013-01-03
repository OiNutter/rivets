from environment import Environment
from engines import EngineRegistry, JSTemplate, CSSTemplate
from processors import ProcessorRegistry, UglipyJSProcessor, SlimmerCSSProcessor

from shift.coffee import CoffeeScriptTemplate
from shift.css import ScssTemplate

EngineRegistry.register_engine('.js',JSTemplate)
EngineRegistry.register_engine('.css',CSSTemplate)
EngineRegistry.register_engine('.coffee',CoffeeScriptTemplate)
EngineRegistry.register_engine('.scss',ScssTemplate)

ProcessorRegistry.register_postprocessor('.js',UglipyJSProcessor)
ProcessorRegistry.register_postprocessor('.css',SlimmerCSSProcessor)