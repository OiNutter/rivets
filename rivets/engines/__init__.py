from registry import EngineRegistry

from lean._coffee import CoffeeScriptTemplate
from lean._css import ScssTemplate
from lean._mako import MakoTemplate
from lean._string import StringTemplate

engine_registry = EngineRegistry()

engine_registry.register_engine('.coffee',CoffeeScriptTemplate)
engine_registry.register_engine('.scss',ScssTemplate)
engine_registry.register_engine('.mako',MakoTemplate)
engine_registry.register_engine('.str',StringTemplate)