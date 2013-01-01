from environment import Environment
from engines import EngineRegistry, JSTemplate, CSSTemplate

from shift.coffee import CoffeeScriptTemplate
from shift.css import ScssTemplate

EngineRegistry.register_engine('.js',JSTemplate)
EngineRegistry.register_engine('.css',CSSTemplate)
EngineRegistry.register_engine('.coffee',CoffeeScriptTemplate)
EngineRegistry.register_engine('.scss',ScssTemplate)