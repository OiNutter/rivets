from environment import Environment
from engines import EngineRegistry, JSTemplate, CSSTemplate
from processors import ProcessorRegistry, UglipyJSProcessor, SlimmerCSSProcessor

from lean.coffee import CoffeeScriptTemplate
from lean.css import ScssTemplate

EngineRegistry.register_engine('.js',JSTemplate)
EngineRegistry.register_engine('.css',CSSTemplate)
EngineRegistry.register_engine('.coffee',CoffeeScriptTemplate)
EngineRegistry.register_engine('.scss',ScssTemplate)

ProcessorRegistry.set_minifier('.js',UglipyJSProcessor)
ProcessorRegistry.set_minifier('.css',SlimmerCSSProcessor)