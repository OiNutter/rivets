Rivets
======

Rivets is a port of [Sprockets](https://github.com/sstephenson/sprockets) to Python. 
At the moment it just has the core functionality, and is probably closer to Sprockets 1.0 than to the
current advanced features 

It's still a work in progress and has not been tested in production yet, but you're
welcome to fork and help get it working quicker if you so wish. At the
moment it will concatenate js and css files, as well as compiling CoffeeScript and Scss,
and minify the output using the appropriate engine. At the moment it is using 
[UglipyJS](https://github.com/OiNutter/uglipyjs) for js files and [Slimmer](http://pypi.python.org/pypi/slimmer/)
for css.

I'm using [Crawl](https://github.com/OiNutter/crawl), the
[Hike](https://github.com/sstephenson/hike) port I wrote to scan for the
assets. That is in a similar situation to Rivets, although slightly more
along in the development cycle, as they are being developed in tandem. I'm also using 
[Lean](https://github.com/OiNutter/lean), another Ruby port, this time of 
[Tilt](https://github.com/rtomayko/tilt) to provide a generic interface to the various templating and
processing modules being used.

Install
-------

```bash
$ pip install rivets
```

See the class docs for each processor and engine in `processors.py` and `engines.py` to find the install command.

Sample Usage
------------

```python
import rivets
env = rivets.Environment()
env.add_path('test/js')
env.compile('blah')
```

Assets
------



Directives
----------

At the moment rivets just uses the `require` directive but I will be adding more to match those available in Sprockets.

Directives are specified in comment blocks at the start of a file:

JS
```javascript
//= require 'jquery'
/*
 *= require 'mustache'
 */
```

CSS
```css
/*
 *= require 'fonts'
 */
```

CoffeeScript
```coffeescript
#= require 'zepto'
```

SCSS
```scss
//= require 'compass'
/*
 * require 'mixins'
 */
```

###Require###

The `require` directive will search for a single file inside the load path and raise an error if it is not found.

Engines
-------

Rivets can compile asset files in other languages that compile to Javascript or CSS. Currently Rivets comes with the following engines.

###CoffeeScript###

CoffeeScript compiles to Javascript and features a cleaner, more Python like syntax as well as handling for function scope binding.

CoffeeScript assets have a `.js.coffee` extension and require the `Python-CoffeeScript` module to be installed.

```bash
$ pip install coffeescript
```

###SCSS###

SCSS compiles to CSS and features a number of enhancements, including rule nesting, mixins and variables, enabling you to write smaller, more easily updateable CSS styles.

SCSS assets have a `.css.scss` extension and require the `pyScss` module to be installed.

```bash
$ pip install pyscss
```

###Adding Your Own Engines###

If you wish to add your own processing engines you can subclass Lean.Template and register the engine for a given extension like so:

```python

from lean.template import Template
import rivets

class FooEngine(Template):
	''' Your Code Here '''

env = rivets.Environment()
env.register_engine('.foo',FooEngine)
```

In this case, assuming FooEngine compiled to Javascript, your files would have the extension `.js.foo`.

Processors
----------

Rivets enables the specification of `Processors` that can be run either before or after a file is compiled and concatentated. `Preprocessors` are run before an asset is processed, and `Postprocessors` are run afterwards. Processors are subclasses of Lean templates and can be registered in the following manner:

```python
from lean.template import Template
import rivets

class FooProcessor(Template):
	''' Your Code Here '''

class BlahProcessor(Template):
	''' Your Code Here '''

env = rivets.Environment()
env.register_preprocessor('.js',FooProcessor)
eng.register_postprocessor('.js',BlahProcessor)
```



License
-------

Copyright 2011 Will McKenzie

Licensed under the MIT License, please see the license file for more
details.
