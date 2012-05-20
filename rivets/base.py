#import rivets modules
from assets import AssetAttributes, BundledAsset, ProcessedAsset, StaticAsset
import caching
import errors
import server
import mime
import processing
import engines
import paths
import fnmatch

import rivets

# import python builtin modules
import os
import re
import copy

class Base(object):
  ''' `Base` class for `Environment` and `Index`. '''

  @property
  def digest_class(self):
    ''' Returns a `Digest` implementation class.
        
        Defaults to `Digest::MD5`.
    '''
    return self._digest_class

  @digest_class.setter
  def digest_class(self,klass):
    ''' Assign a `Digest` implementation class. This maybe any Ruby
        `Digest::` implementation such as `Digest::MD5` or
        `Digest::SHA1`.

        environment.digest_class = Digest::SHA1
    '''
    self.expire_index()
    self._digest_class = klass

  @property
  def version(self):
    ''' The `Environment#version` is a custom value used for manually
        expiring all asset caches.
        
        Sprockets is able to track most file and directory changes and
        will take care of expiring the cache for you. However, its
        impossible to know when any custom helpers change that you mix
        into the `Context`.
      
        It would be wise to increment this value anytime you make a
        configuration change to the `Environment` object.
    '''
    return self._version

  @version.setter
  def version(self,version):
    ''' Assign an environment version.
        
          environment.version = '2.0'
    '''
    self.expire_index()
    self._version = version

  def digest(self):
    ''' Returns a `Digest` instance for the `Environment`.
        
        This value serves two purposes. If two `Environment`s have the
        same digest value they can be treated as equal. This is more
        useful for comparing environment states between processes rather
        than in the same. Two equal `Environment`s can share the same
        cached assets.
        
        The value also provides a seed digest for all `Asset`
        digests. Any change in the environment digest will affect all of
        its assets.
    '''

    # Compute the initial digest using the implementation class. The
    # Sprockets release version and custom environment version are
    # mixed in. So any new releases will affect all your assets.
    if not self._digest:
      self._digest = self.digest().update(rivets.VERSION).update(str(self.version))

    # Returned a dupped copy so the caller can safely mutate it with `.update`
    return copy.copy(self._digest)

    # Get and set `Logger` instance.
    logger

  @property
  def context_class(self):
    ''' Get `Context` class. '''
    return self._context_class

  @property
  def cache(self):
    ''' Get persistent cache store '''
    return self._cache

  @cache.setter
  def cache(self,cache):
    ''' Set persistent cache store
        The cache store must implement a pair of getters and
        setters. Either `get(key)`/`set(key, value)`,
        `[key]`/`[key]=value`, `read(key)`/`write(key, value)`.
    '''
    self.expire_index()
    self._cache = cache

  def prepend_path(self,path):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    paths.prepend_path(path)

  def append_path(path):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    paths.append_path(path)

  def clear_paths(self):
    ''' Overrides the global behavior to expire the index
        self.expire_index()
    '''
    self.expire_index()
    paths.clear_paths()

  def resolve(self, logical_path, options = {},block=None):
    ''' If a block is given, preform an iterable search '''
    if block:
      args = self.attributes_for(logical_path).search_paths + [options]
      path = self.trail.find(*args)
      return block(os.path.abspath(path))
    else:
      pathname = resolve(logical_path, options)
      return pathname

  def register_mime_type(self,mime_type, ext):
    ''' Register a new mime type.
        
        Overrides the global behavior to expire the index
    '''
    self.expire_index()
    self.trail.append_extension(ext)
    mime.register_mime_type(mime_type,ext)

  def register_engine(self, ext, klass):
    ''' Registers a new Engine `klass` for `ext`.
        
        Overrides the global behavior to expire the index
    '''
    self.expire_index()
    self.add_engine_to_trail(ext, klass)
    engines.register_engine(ext,klass)

  def register_preprocessor(self,mime_type, klass, block=None):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    procesing.register_preprocessor(mime_type,klass,block)

  def unregister_preprocessor(self, mime_type, klass):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    processing.unregister_preprocessor(mime_type,klass)

  def register_postprocessor(self,mime_type, klass, block=None):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    processing.register_postprocessor(mime_type,klass,block)

  def unregister_postprocessor(self,mime_type, klass):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    processing.unregister_postprocessor(mime_type,klass)

  def register_bundle_processor(self,mime_type, klass, block=None):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    processing.register_bundle_processor(mime_type,klass,block)

  def unregister_bundle_processor(self,mime_type, klass):
    ''' Overrides the global behavior to expire the index '''
    self.expire_index()
    processing.unregister_bundle_processor(mime_type,klass)

  def index(self):
    raise NotImplementedError

  @property
  def default_external_encoding(self):
    return self._default_external_encoding if self._default_external_encoding else 'UTF-8'

  @default_external_encoding.setter()
  def default_external_encoding(self,encoding):
    self._default_external_encoding = encoding

  def entries(self,pathname):
    ''' Works like `Dir.entries`.
        
        Subclasses may cache this method.
    '''
    return self.trail.entries(pathname)

  def stat(self,path):
    ''' Works like `File.stat`.
        
        Subclasses may cache this method.
    '''
    return self.trail.stat(path)

  def file_digest(self,path):
    ''' Read and compute digest of filename.
      
        Subclasses may cache this method.
    '''
    stat = self.stat(path)
    if stat:
        # If its a file, digest the contents
        if os.path.isfile(stat):
          return self.digest.file(str(path))

        # If its a directive, digest the list of filenames
        elif os.path.isdir(stat):
          contents = self.entries(path).join(',')
          return self.digest.update(contents)

  def attributes_for(self,path):
    ''' Internal. Return a `AssetAttributes` for `path`. '''
    return AssetAttributes(self, path)

  def content_type_of(self,path):
    ''' Internal. Return content type of `path` '''
    return self.attributes_for(path).content_type

  def find_asset(self,path, options = {}):
    ''' Find asset by logical path or expanded path. '''
    logical_path = path
    pathname     = path

    if os.path.isabs(pathname.absolute):
        if not self.stat(pathname):
          return self.stat(pathname)
        logical_path = self.attributes_for(pathname).logical_path
    else:
      try:
        pathname = resolve(logical_path)
      except IOError, e:
        return None

      return self.build_asset(logical_path, pathname, options)

  def each_entry(self,root, block):
    
      paths = []
      for filename in self.entries(root).sort():
        path = os.path.join(root,filename)
        paths.append(path)

        if os.path.isdir(self.stat(path)):
          self.each_entry(path, block=lambda x: paths.append(x))

      for path in paths.sort(key=lambda x: [int(y) for y in x.split('.')]):
        block(path)

  def each_file(self,block):
    def temp(path):
        if not os.path.isdir(self.stat(path)):
          block(path)
    for root in self.paths:
      self.each_entry(root, temp)

  def each_logical_path(self,block,*args):
        
    filters = flatten(args)
    files = {}
    def temp(filename):
        logical_path = self.logical_path_for_filename(filename, filters)
        if logical_path:
          if not files[logical_path]:
            block(logical_path)
            files[logical_path] = True

    self.each_file(temp)

  def expire_index(self,):
    ''' Clear index after mutating state. Must be implemented by the subclass. '''
    raise NotImplementedError

  def build_asset(self,logical_path, pathname, options):
    pathname = os.path.normpath(pathname)

    # If there are any processors to run on the pathname, use
    # `BundledAsset`. Otherwise use `StaticAsset` and treat is as binary.
    if len(self.attributes_for(pathname).processors) >0 :
      if not options['bundle']:
        self.circular_call_protection(pathname, lambda x: ProcessedAsset(self.index, logical_path, x))
      else:
        BundledAsset(self.index, logical_path, pathname)
    else:
        StaticAsset(self.index, logical_path, pathname)

  def cache_key_for(self,path, options):
    "%s:%s" % (path, 1 if options['bundle'] else 0)

  def circular_call_protection(self,path,block=None):
    reset = Thread.current['sprockets_circular_calls']
    if not Thread.current['sprockets_circular_calls']:
      Thread.current['sprockets_circular_calls'] = Set.new
    try:
      if path in self.calls:
        raise CircularDependencyError("%s has already been required" % path)
    
      self.calls.append(path)

      block()
    finally:
      if reset:
        Thread.current['sprockets_circular_calls'] = None 

  def logical_path_for_filename(self,filename, filters):
    logical_path = str(self.attributes_for(filename).logical_path)

    if self.matches_filter(filters, logical_path):
      return logical_path

    # If filename is an index file, retest with alias
    if re.sub(r"[^\.]+",os.path.basename(logical_path),0)[0] == 'index':
      path = logical_path.sub(r"\/index\.", '.')
      if self.matches_filter(filters, path):
            return path
      return None

  def matches_filter(self,filters, filename):
    if len(filters)==0:
      return True

    for filter in filters:
      if isinstance(filter,re.RegexObject):
        if filter.match(filename):
          return True
      elif hasattr(filter,'call') and callable(filter,'call'):
        if filter.call(filename):
          return True
      else:
        if fnmatch.fnmatch(str(filter), filename):
          return True


def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
