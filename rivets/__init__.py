# import python modules
import os
import shift
import crawl

# import rivets modules
import engines
import mime
import processing

trail = crawl.Trail.new(os.path.abspath(__file__))

mime.register_mime_type('text/css', '.css')
mime.register_mime_type('application/javascript', '.js')

from directive_processor import DirectiveProcessor
processing.register_preprocessor('text/css', DirectiveProcessor)
processing.register_preprocessor('application/javascript', DirectiveProcessor)

from safety_colons import SafetyColons
processing.register_postprocessor('application/javascript', SafetyColons)

from charset_normalizer import CharsetNormalizer
processing.register_bundle_processor('text/css', CharsetNormalizer)

# register required Shift engines

# CoffeeScript
engines.register_engine('.coffee',shift.coffee.CoffeeScriptTemplate)

# Scss
engines.register_engine('.scss',shift.css.ScssTemplate)

