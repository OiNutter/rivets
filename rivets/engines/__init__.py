from registry import EngineRegistry

from lean._coffee import CoffeeScriptTemplate
from lean._css import ScssTemplate
from lean._mako import MakoTemplate

EngineRegistry.register_engine('.coffee',CoffeeScriptTemplate)
EngineRegistry.register_engine('.scss',ScssTemplate)
EngineRegistry.register_engine('.mako',MakoTemplate)