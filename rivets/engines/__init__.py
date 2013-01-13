from registry import EngineRegistry

from lean.coffee import CoffeeScriptTemplate
from lean.css import ScssTemplate

EngineRegistry.register_engine('.coffee',CoffeeScriptTemplate)
EngineRegistry.register_engine('.scss',ScssTemplate)