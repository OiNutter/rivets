Rivets
======

Rivets is an attempt to rewrite
[Sprockets](https://github.com/sstephenson/sprockets) for Python. At the
moment it's a pretty basic implementation but I'm hoping to get it up to
the fully featured levels of the original eventually.

It's still a work in progress and not suitable for live use, but you're
welcome to fork and help get it working quicker if you so wish. At the
moment it will concatenate js and css files and I'm working on adding
support for CoffeeScript. Next up will be Sass files, and then adding
minification.

I'm using [Crawl](https://github.com/OiNutter/crawl), the
[Hike](https://github.com/sstephenson/hike) port I wrote to scan for the
assets. That is in a similar situation to Rivets, although slightly more
along in the development cycle, as they are being developed in tandem.

Requirements
------------

* Crawl
* Python-Coffeescript

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
