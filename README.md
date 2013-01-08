Rivets
======

Rivets is an attempt to rewrite
[Sprockets](https://github.com/sstephenson/sprockets) for Python. At the
moment it's a pretty basic implementation but I'm hoping to get it up to
the fully featured levels of the original eventually.

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

Requirements
------------

* Crawl
* Lean
* PySCSS
* Slimmer

To use the various processors you will need to make sure you have the required modules installed. I'm leaving
that to you so I don't pollute your system with modules you'll never use. If you wish to keep the existing minifiers
run the following in the command line:

```bash
pip install uglipyjs
pip install slimmer
```

To process CoffeeScript and Scss you will also need to run the following:

```bash
pip install CoffeeScript
pip install pyScss
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

License
-------

Copyright 2011 Will McKenzie

Licensed under the MIT License, please see the license file for more
details.
