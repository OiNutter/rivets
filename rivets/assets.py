import errors
import os
import zlib
import sys
import datetime
import collections
import re
import shutil

class Asset(object):
  ''' `Asset` is the base class for `BundledAsset` and `StaticAsset`. '''
    
  def from_hash(self,environment, hash):
    # Internal initializer to load `Asset` from serialized `Hash`.
    try:
      if not isinstance(hash,dict):
        return False

      klass = None
      if hash['class'] == 'BundledAsset':
        klass = BundledAsset
      elif hash['class'] == 'ProcessedAsset':
        klass = ProcessedAsset
      elif hash['class'] == 'StaticAsset':
        klass = StaticAsset

      if klass:
        asset = klass.allocate()
        asset.init_with(environment, hash)
        return asset
    except:
      raise errors.UnserializeError()
      return None

  def initialize(self,environment, logical_path, pathname):
    self.root         = environment.root
    self.logical_path = str(logical_path)
    self.pathname     = os.path.normpath(pathname)
    self.content_type = environment.content_type_of(pathname)
    self.mtime        = environment.stat(pathname).mtime
    self.length       = environment.stat(pathname).size
    self.digest       = environment.file_digest(pathname).hexdigest()

  def init_with(self,environment, coder):
    '''Initialize `Asset` from serialized `Hash` '''
    self.root = environment.root

    self.logical_path = coder['logical_path']
    self.content_type = coder['content_type']
    self.digest       = coder['digest']

    pathname = coder['pathname']
    if pathname:
      # Expand `$root` placeholder and wrapper string in a `Pathname`
      self.pathname = os.path.normpath(self.expand_root_path(pathname))

    mtime = coder['mtime']
    if mtime:
      # Parse time string
      self.mtime = datetime.datetime.strtime(mtime)

    length = coder['length']
    if length:
      # Convert length to an `Integer`
      self.length = int(length)

  def encode_with(self,coder):
    ''' Copy serialized attributes to the coder object '''

    coder['class']        = re.sub(r"Sprockets::",self.__name__, "")
    coder['logical_path'] = self.logical_path
    coder['pathname']     = str(self.relativize_root_path(self.pathname))
    coder['content_type'] = self.content_type
    coder['mtime']        = self.mtime.iso8601
    coder['length']       = self.length
    coder['digest']       = self.digest

  def digest_path(self):
    ''' Return logical path with digest spliced in.
    
       "foo/bar-37b51d194a7513e45b56f6524f2d51f2.js"
    '''
    return re.sub(r"\.(\w+)$",self.logical_path,"%s.\1" % self.digest)

  def dependencies(self):
    ''' Return an `Array` of `Asset` files that are declared dependencies. '''
    return []

  def to_a(self):
    ''' Expand asset into an `Array` of parts.
    
      Appending all of an assets body parts together should give you
      the asset's contents as a whole.
    
      This allows you to link to individual files for debugging
      purposes.
    '''
    return [self]

  def body(self):
    ''' `body` is aliased to source by default if it can't have any dependencies. '''
    return self.source

  def to_s(self):
    ''' Return `String` of concatenated source. '''
    return self.source

  def each(self):
    ''' Add enumerator to allow `Asset` instances to be used as Rack
        compatible body objects.
    '''
    return self.to_s()

  def is_fresh(self,environment):
    ''' Checks if Asset is fresh by comparing the actual mtime and
        digest to the inmemory model.
        
        Used to test if cached models need to be rebuilt.
    '''
    #Check current mtime and digest
    return self.is_dependency_fresh(environment, self)

  def is_stale(self,environment):
    ''' Checks if Asset is stale by comparing the actual mtime and
        digest to the inmemory model.
      
        Subclass must override `fresh?` or `stale?`.
    '''
    return not self.is_fresh(environment)

  def write_to(self,filename, options = None):
    ''' Save asset to disk. '''
    
    try:
      if not options:
        options = {}
    
      # Gzip contents if filename has '.gz'
      file,extname = os.path.splitext(filename)
      options['compress'] = True if extname == 'gz' else False

      os.makedirs(os.dirname(filename))

      f = open("%s+"% filename, 'wb')
      if options['compress']:
        # Run contents through `Zlib`
        gz = zlib.compress(self.to_s(),9)
        f.mtime = datetime.datetime.mktime(self.mtime.timetuple())
        f.write(gz)
        f.close()
      else:
        # Write out as is
        f.write(self.to_s())
        f.close()

        # Atomic write
        os.rename("%s+"%filename, filename)

        # Set mtime correctly
        os.utime(filename,(self.mtime, self.mtime))

        return None
    finally:
      # Ensure tmp file gets cleaned up
      if os.path.exists("%s+"%filename):
        os.remove("%s+"%filename) 

  def inspect(self):
      ''' Pretty inspect '''
      return "#<%s:0x%s pathname=%s, mtime=%s, digest=%s>" % (self.__class__,hex(id(self)),str(self.pathname),str(self.mtime),str(self.digest))

  def hash(self):
    return hash(self.digest)

  def eql(self,other):
    return other.__class__ == self.__class__ and other.logical_path == self.logical_path and datetime.datetime.mktime(other.mtime.timetuple) == datetime.datetime.mktime(self.mtime.timetuple) and other.digest == self.digest
      
  def dependency_paths(self):
    ''' Internal: String paths that are marked as dependencies after processing.
    
        Default to an empty `Array`.
    '''
    if not self.dependency_paths:
      self.dependency_paths = []
    return self.dependency_paths

  def required_assets(self):
    ''' Internal: `ProccessedAsset`s that are required after processing.
      
        Default to an empty `Array`.
    '''
    if not self._required_assets:
      self._required_assets = []
    return self._required_assets

  def relative_pathname(self):
    ''' Get pathname with its root stripped. '''
    if not self.relative_pathname:
      self.relative_pathname = self.relativize_root_path(self.pathname)
    return self.relative_pathname

  def expand_root_path(self,path):
    ''' Replace `$root` placeholder with actual environment root. '''
    return re.sub(r"^\$root",self.root,str(path))

  def relativize_root_path(self,path):
    ''' Replace actual environment root with `$root` placeholder. '''
    return re.sub(r"^%s" % re.escape(self.root), '$root',str(path))

  def is_dependency_fresh(self,environment, dep):
    ''' Check if dependency is fresh.
      
        `dep` is a `Hash` with `path`, `mtime` and `hexdigest` keys.
      
        A `Hash` is used rather than other `Asset` object because we
        want to test non-asset files and directories.
    '''
    path, mtime, hexdigest = str(dep.pathname), dep.mtime, dep.digest

    stat = environment.stat(path)

    # If path no longer exists, its definitely stale.
    if not stat:
      return False

    # Compare dependency mime to the actual mtime. If the
    # dependency mtime is newer than the actual mtime, the file
    # hasn't changed since we created this `Asset` instance.
    #
    # However, if the mtime is newer it doesn't mean the asset is
    # stale. Many deployment environments may recopy or recheckout
    # assets on each deploy. In this case the mtime would be the
    # time of deploy rather than modified time.
    if mtime >= stat.mtime:
      return True

    digest = environment.file_digest(path)

    # If the mtime is newer, do a full digest comparsion. Return
    # fresh if the digests match.
    if hexdigest == digest.hexdigest:
      return True

    # Otherwise, its stale.
    return False

class BundledAsset(Asset):

  def __init__(self,environment, logical_path, pathname):
    super(BundledAsset,environment, logical_path, pathname)

    self.processed_asset = environment.find_asset(pathname, bundle = False)
    self.required_assets = self.processed_asset.required_assets

    self.source = ""

    # Explode Asset into parts and gather the dependency bodies
    for dependency in self.to_a():
      self.source << str(dependency)

    # Run bundle processors on concatenated source
    context = environment.context_class(environment, logical_path, pathname)
    self.source = context.evaluate(pathname, data = self.source, processors = environment.bundle_processors(self.content_type))

    self.mtime  = max(map(lambda x: x.mtime, self.to_a()))
    self.length = sys.getsizeof(self.source)
    self.digest = environment.digest.update(self.source).hexdigest()

  def init_with(self,environment, coder):
    ''' Initialize `BundledAsset` from serialized `Hash`. '''
    super(BundledAsset,environment,coder)

    self.processed_asset = environment.find_asset(self.pathname, bundle = False)
    self.required_assets = self.processed_asset.required_assets()

    if self.processed_asset.dependency_digest != coder['required_assets_digest']:
      raise errors.UnserializeError("processed asset belongs to a stale environment")

    self.source = coder['source']

  def encode_with(self,coder):
    ''' Serialize custom attributes in `BundledAsset`. '''
    super(BundledAsset,coder)

    coder['source'] = self.source
    coder['required_assets_digest'] = self.processed_asset.dependency_digest()

  def body(self):
    ''' Get asset's own processed contents. Excludes any of its required
        dependencies but does run any processors or engines on the
        original file.
    '''
    return self.processed_asset.source

  def dependencies(self):
    ''' Return an `Array` of `Asset` files that are declared dependencies. '''
    return [a for a in self.to_a() if not a.eql(self.processed_asset)]

  def to_a(self):
    ''' Expand asset into an `Array` of parts. '''
    return self.required_assets

  def is_fresh(self, environment):
    ''' Checks if Asset is stale by comparing the actual mtime and
        digest to the inmemory model.
    '''
    return self.processed_asset.is_fresh(environment)

class ProcessedAsset(Asset):
    
  def __init__(self,environment, logical_path, pathname):
    super(ProcessedAsset,environment,logical_path,pathname)

    start_time = float(datetime.datetime.now())

    self.context = environment.context_class.new(environment, logical_path, pathname)
    self.source = self.context.evaluate(pathname)
    self.length = sys.getsizeof(self.source)
    self.digest = environment.digest.update(self.source).hexdigest()

    self.build_required_assets(environment, self.context)
    self.build_dependency_paths(environment, self.context)

    self.dependency_digest = self.compute_dependency_digest(environment)

    elapsed_time = int((float(datetime.datetime.now()) - start_time) * 1000)
    environment.logger.info("Compiled %s  (%dms)  (pid %s)" % (logical_path,elapsed_time,os.getpid()))

  def init_with(self,environment, coder):
    super(ProcessedAsset,environment,coder)

    self.source = coder['source']
    self.dependency_digest = coder['dependency_digest']

    def map_paths(p):
      p = self.expand_root_path(p)

      result = False
      for path in environment.paths:
        if path in p:
          result = True

      if not result:
        raise errors.UnserializeError("%s isn't in paths" % p)

      return self if p == str(self.pathname) else environment.find_asset(p, bundle = False)

    self.required_assets = map(map_paths,coder['required_paths'])

    self.dependency_paths = map(lambda h: DependencyFile(self.expand_root_path(h['path']), h['mtime'], h['digest']), coder['dependency_paths'])

  def encode_with(self,coder):
    ''' Serialize custom attributes in `BundledAsset`. '''
    super(ProcessedAsset,coder)

    coder['source'] = self.source
    coder['dependency_digest'] = self.dependency_digest

    coder['required_paths'] = map(lambda a: str(self.relativize_root_path(a.pathname)),self.required_assets)
    
    def to_dep_dict(d):
      return {
        "path":str(self.relativize_root_path(d.pathname)),
        "mtime":d.mtime.isoformat(),
        "digest":d.digest
      }

    coder['dependency_paths'] = map(to_dep_dict,self.dependency_paths)

  def is_fresh(self,environment):
    ''' Checks if Asset is stale by comparing the actual mtime and
        digest to the inmemory model.
    '''
    # Check freshness of all declared dependencies
    result = False
    for dep in self.dependency_paths:
      result = self.is_dependency_fresh(environment, dep)
    
    return result

DependencyFileParent = collections.namedtuple('DependencyFileParent',['pathname','mtime','digest'])
class DependencyFile(DependencyFileParent):
  def __init__(self,pathname, mtime, digest):
    pathname = os.path.normpath(pathname)
    if isinstance(mtime,str):
      mtime = datetime.datetime.strptime(mtime)
    super(DependencyFile,pathname,mtime,digest)

  def eql(self,other):
    return isinstance(other,DependencyFile) and self.pathname == other.pathname and self.mtime == other.mtime and self.digest == other.digest

  def hash(self):
    return hash(str(self.pathname))

  def build_required_assets(self,environment, context):
    self._required_assets = self.resolve_dependencies(environment, context._required_paths + [str(self.pathname)]) - self.resolve_dependencies(environment, context._stubbed_assets.to_a())

  def resolve_dependencies(self,environment, paths):
    assets = []
    cache  = {}

    for path in paths:
      if path == str(self.pathname):
      
        if not cache[self]:
          cache[self] = True
          assets.append(self)

      elif environment.find_asset(path, bundle = False):
          asset = environment.find_asset(path, bundle = False)
          for asset_dependency in asset.required_assets():
              if not cache[asset_dependency]:
                cache[asset_dependency] = True
                assets.append(asset_dependency)
      
      return assets

  def build_dependency_paths(self,environment, context):
    dependency_paths = {}

    for path in context._dependency_paths:
      dep = DependencyFile(path, environment.stat(path).mtime, environment.file_digest(path).hexdigest())
      dependency_paths[dep] = True
     
    for path in context._dependency_assets:
      if path == str(self.pathname):
        dep = DependencyFile(self.pathname, environment.stat(path).mtime, environment.file_digest(path).hexdigest())
        dependency_paths[dep] = True
      elif environment.find_asset(path, bundle = False):
        asset = environment.find_asset(path, bundle = False)
        for d in asset.dependency_paths:
          dependency_paths[d] = True

    dependency_paths = dependency_paths.keys()
    return dependency_paths

  def compute_dependency_digest(self,environment):
    return reduce(lambda digest, asset: digest.update(asset.digest),self._required_assets).hexdigest()
    

class StaticAsset(Asset):
  ''' `StaticAsset`s are used for files that are served verbatim without
      any processing or concatenation. These are typical images and
      other binary files.
  '''

  def source(self):
    ''' Returns file contents as its `source`. '''
    
    # File is read everytime to avoid memory bloat of large binary files
    return open(self.pathname,'rb').read()

  def to_path(self):
    ''' Implemented for Rack SendFile support. '''
    return str(self.pathname)

  def write_to(self,filename, options = None):
    ''' Save asset to disk. ''' 
    try:
      if not options:
        options = {}

      # Gzip contents if filename has '.gz'
      if not options['compress']:
        filename,ext = os.path.splitext(filename)
        if ext == 'gz':
          options['compress'] = True

      os.makedirs(os.path.dirname(filename))

      if options['compress']:
        # Open file and run it through `Zlib`
        buf = open(self.pathname,'rb').read(16384)
        wr =open("%s+"%filename, 'wb')
        gz = gz = zlib.compress(buf,9)
        wr.mtime = datetime.datetime.mktime(self.mtime.timetuple())
        wr.write(gz)
        wr.close()
      else:
        # If no compression needs to be done, we can just copy it into place.
        shutil.copy(self.pathname, "%s+"%filename)

      # Atomic write
      os.rename("%s+" % filename, filename)

      # Set mtime correctly
      os.utime(filename,(self.mtime, self.mtime))

      return None
    finally:
      # Ensure tmp file gets cleaned up
      if os.path.exists("%s+" % filename):
        os.remove("%s+" % filename) 