Rivets
======

[![Build Status](https://travis-ci.org/OiNutter/rivets.png)](https://travis-ci.org/OiNutter/rivets)

Rivets is a Python port of the [Rivets](https://github.com/sstephenson/sprockets) 
Ruby library for compiling and serving web assets.
It features declarative dependency management for JavaScript and CSS
assets, as well as a powerful preprocessor pipeline that allows you to
write assets in languages like CoffeeScript and SCSS.

# Installation #

Install rivets with pip:

``` bash
$ pip install rivets
```

# Understanding the Rivets Environment #

You'll need an instance of the `rivets.Environment` class to
access and serve assets from your application.

The Rivets `Environment` has methods for retrieving and serving
assets, manipulating the load path, and registering processors. It is
also a CherryPy compatible Route Dispatcher application that can be mounted at a 
URL to serve assets over HTTP.

## The Load Path ##

The *load path* is an ordered list of directories that Rivets uses
to search for assets.

In the simplest case, a Rivets environment's load path will consist
of a single directory containing your application's asset source
files. When mounted, the environment will serve assets from this
directory as if they were static files in your public root.

The power of the load path is that it lets you organize your source
files into multiple directories -- even directories that live outside
your application -- and combine those directories into a single
virtual filesystem. That means you can easily bundle JavaScript, CSS
and images into a python library and import them into your application.

### Manipulating the Load Path ###

To add a directory to your environment's load path, use the
`append_path` and `prepend_path` methods. Directories at the beginning
of the load path have precedence over subsequent directories.

``` python
environment = rivets.Environment()
environment.append_path('app/assets/javascripts')
environment.append_path('lib/assets/javascripts')
environment.append_path('vendor/assets/jquery')
```

In general, you should append to the path by default and reserve
prepending for cases where you need to override existing assets.

## Accessing Assets ##

Once you've set up your environment's load path, you can mount the
environment as a Rack server and request assets via HTTP. You can also
access assets programmatically from within your application.

### Logical Paths ###

Assets in Rivets are always referenced by their *logical path*.

The logical path is the path of the asset source file relative to its
containing directory in the load path. For example, if your load path
contains the directory `app/assets/javascripts`:

<table>
  <tr>
    <th>Asset source file</th>
    <th>Logical path</th>
  </tr>
  <tr>
    <td>app/assets/javascripts/application.js</td>
    <td>application.js</td>
  </tr>
  <tr>
    <td>app/assets/javascripts/models/project.js</td>
    <td>models/project.js</td>
  </tr>
</table>

In this way, all directories in the load path are merged to create a
virtual filesystem whose entries are logical paths.

### Serving Assets Over HTTP ###

When you mount an environment, all of its assets are accessible as
logical paths underneath the *mount point*. For example, if you mount
your environment at `/assets` and request the URL
`/assets/application.js`, Rivets will search your load path for the
file named `application.js` and serve it.

To mount the environment in CherryPy you will need to create an instance of the environment and map the route to 
it's call action:

``` python
import rivets

environment = rivets.Environment()
environment.append_path('app/assets/javascripts')
environment.append_path('app/assets/stylesheets')

d = cherrypy.dispatch.RoutesDispatcher()
d.connect('assets','/assets/:path',controller = env, action='run')
```

### Accessing Assets Programmatically ###

You can use the `find_asset` method (aliased as `[]`) to retrieve an
asset from a Rivets environment. Pass it a logical path and you'll
get a `BundledAsset` instance back:

``` python
environment['application.js']
# => #<rivets.assets.bundled_asset.BundledAsset object ...>
```

Call `to_string` on the resulting asset or cast to `str` to access its contents, `length` to
get its length in bytes, `mtime` to query its last-modified time, and
`pathname` to get its full path on the filesystem.

# Using Engines #

Asset source files can be written in another language, like SCSS or
CoffeeScript, and automatically compiled to CSS or JavaScript by
Rivets. Compilers for these languages are called *engines*.

Engines are specified by additional extensions on the asset source
filename. For example, a CSS file written in SCSS might have the name
`layout.css.scss`, while a JavaScript file written in CoffeeScript
might have the name `dialog.js.coffee`.

## Styling with SCSS ##

[Sass](http://sass-lang.com/) is a language that compiles to CSS and
adds features like nested rules, variables, mixins and selector
inheritance.

You will need to install [pyScss](https://github.com/Kronuz/pyscss) to use Scss
in your application.

Rivets currently only supports the newer Scss syntax. Unfortunately due to differences between
pyScss's implementation of Scss and the original Ruby gem's implementation, not all Sass features 
are properly supported. I'm going to be looking at doing a more consistent port of the original library
to enable Rivets to override the importers to handle caching better etc.

## Scripting with CoffeeScript ##

[CoffeeScript](http://jashkenas.github.com/coffee-script/) is a
language that compiles to the "good parts" of JavaScript, featuring a
cleaner syntax with array comprehensions, classes, and function
binding.

You'll need to have the [Python-CoffeeScript](https://github.com/doloopwhile/python-coffeescript) module installed
on your system to use the CoffeeScript processing.

To write JavaScript assets with CoffeeScript, use the extension
`.js.coffee`.

## Invoking Python with Mako ##

Rivets provides a Mako engine for preprocessing assets using
embedded Python code. Append `.mako` to a CSS or JavaScript asset's
filename to enable the Mako engine.

**Note**: Rivets processes multiple engine extensions in order from
  right to left, so you can use multiple engines with a single
  asset. For example, to have a CoffeeScript asset that is first
  preprocessed with Mako, use the extension `.js.coffee.mako`.

Python code embedded in an asset is evaluated in the context of a
`rivets.Context` instance for the given asset. Common uses for Mako
include:

- embedding another asset as a Base64-encoded `data:` URI with the
  `asset_data_uri` helper
- inserting the URL to another asset, such as with the `asset_path`
  helper provided by the Rivets CherryPy plugin
- embedding other application resources, such as a localized string
  database, in a JavaScript asset via JSON
- embedding version constants loaded from another file

# Managing and Bundling Dependencies #

You can create *asset bundles* -- ordered concatenations of asset
source files -- by specifying dependencies in a special comment syntax
at the top of each source file.

Rivets reads these comments, called *directives*, and processes
them to recursively build a dependency graph. When you request an
asset with dependencies, the dependencies will be included in order at
the top of the file.

## The Directive Processor ##

Rivets runs the *directive processor* on each CSS and JavaScript
source file. The directive processor scans for comment lines beginning
with `=` in comment blocks at the top of the file.

```
//= require jquery
//= require jquery-ui
//= require backbone
//= require_tree .
```

The first word immediately following `=` specifies the directive
name. Any words following the directive name are treated as
arguments. Arguments may be placed in single or double quotes if they
contain spaces, similar to commands in the Unix shell.

**Note**: Non-directive comment lines will be preserved in the final
  asset, but directive comments are stripped after
  processing. Rivets will not look for directives in comment blocks
  that occur after the first line of code.

### Supported Comment Types ###

The directive processor understands comment blocks in three formats:

```
/* Multi-line comment blocks (CSS, SCSS, JavaScript)
*= require foo
*/

// Single-line comment blocks (SCSS, JavaScript)
//= require foo

# Single-line comment blocks (CoffeeScript)
#= require foo
```

## Rivets Directives ##

You can use the following directives to declare dependencies in asset
source files.

For directives that take a *path* argument, you may specify either a
logical path or a relative path. Relative paths begin with `./` and
reference files relative to the location of the current file.

### The `require` Directive ###

`require` *path* inserts the contents of the asset source file
specified by *path*. If the file is required multiple times, it will
appear in the bundle only once.

### The `include` Directive ###

`include` *path* works like `require`, but inserts the contents of the
specified source file even if it has already been included or
required.

### The `require_directory` Directive ###

`require_directory` *path* requires all source files of the same
format in the directory specified by *path*. Files are required in
alphabetical order.

### The `require_tree` Directive ###

`require_tree` *path* works like `require_directory`, but operates
recursively to require all files in all subdirectories of the
directory specified by *path*.

### The `require_self` Directive ###

`require_self` tells Rivets to insert the body of the current
source file before any subsequent `require` or `include` directives.

### The `depend_on` Directive ###

`depend_on` *path* declares a dependency on the given *path* without
including it in the bundle. This is useful when you need to expire an
asset's cache in response to a change in another file.

### The `stub` Directive ###

`stub` *path* allows dependency to be excluded from the asset bundle.
The *path* must be a valid asset and may or may not already be part
of the bundle. Once stubbed, it is blacklisted and can't be brought
back by any other `require`.

# Development #

## Contributing ##

The Rivets source code is [hosted on
GitHub](https://github.com/oinutter/sprockets). You can check out a
copy of the latest code using Git:

``` bash
$ git clone https://github.com/oinutter/rivets.git
```

If you've found a bug or have a question, please open an issue on the
[Rivets issue
tracker](https://github.com/oinutter/rivets/issues). Or, clone
the Rivets repository, write a failing test case, fix the bug and
submit a pull request.

