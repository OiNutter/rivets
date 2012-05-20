import errors
import os
import zlib

import datetime

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

    length = bytesize

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
      self.pathname = os.path.normpath(expand_root_path(pathname))

    mtime = coder['mtime']
    if mtime:
      # Parse time string
      self.mtime = datetime.datetime.strtime(mtime)
      end

    length = coder['length']
    if length:
      # Convert length to an `Integer`
      self.length = int(length)

  def encode_with(coder):
    ''' Copy serialized attributes to the coder object '''

    coder['class']        = re.sub(r"Sprockets::",self.__name__, "")
    coder['logical_path'] = logical_path
    coder['pathname']     = str(relativize_root_path(pathname))
    coder['content_type'] = content_type
    coder['mtime']        = mtime.iso8601
    coder['length']       = length
    coder['digest']       = digest

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
    return source

  def to_s(self):
    ''' Return `String` of concatenated source. '''
    return source

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
    return is_dependency_fresh(environment, self)

  def is_stale(self,environment):
    ''' Checks if Asset is stale by comparing the actual mtime and
        digest to the inmemory model.
      
        Subclass must override `fresh?` or `stale?`.
    '''
    return not self.is_fresh(environment)

  def write_to(self,filename, options = None):
    ''' Save asset to disk. '''
     
    if not options:
      options = {}
    
    # Gzip contents if filename has '.gz'
    file,extname = os.path.splitext(filename)
    options['compress'] = True if extname == 'gz' else False

    FileUtils.mkdir_p File.dirname(filename)

      File.open("#{filename}+", 'wb') do |f|
        if options[:compress]
          # Run contents through `Zlib`
          gz = Zlib::GzipWriter.new(f, Zlib::BEST_COMPRESSION)
          gz.mtime = mtime.to_i
          gz.write to_s
          gz.close
        else
          # Write out as is
          f.write to_s
          f.close
        end
      end

      # Atomic write
      FileUtils.mv("#{filename}+", filename)

      # Set mtime correctly
      File.utime(mtime, mtime, filename)

      nil
    ensure
      # Ensure tmp file gets cleaned up
      FileUtils.rm("#{filename}+") if File.exist?("#{filename}+")
    end

    # Pretty inspect
    def inspect
      "#<#{self.class}:0x#{object_id.to_s(16)} " +
        "pathname=#{pathname.to_s.inspect}, " +
        "mtime=#{mtime.inspect}, " +
        "digest=#{digest.inspect}" +
        ">"
    end

    def hash
      digest.hash
    end

    # Assets are equal if they share the same path, mtime and digest.
    def eql?(other)
      other.class == self.class &&
        other.logical_path == self.logical_path &&
        other.mtime.to_i == self.mtime.to_i &&
        other.digest == self.digest
    end
    alias_method :==, :eql?

    protected
      # Internal: String paths that are marked as dependencies after processing.
      #
      # Default to an empty `Array`.
      def dependency_paths
        @dependency_paths ||= []
      end

      # Internal: `ProccessedAsset`s that are required after processing.
      #
      # Default to an empty `Array`.
      def required_assets
        @required_assets ||= []
      end

      # Get pathname with its root stripped.
      def relative_pathname
        @relative_pathname ||= Pathname.new(relativize_root_path(pathname))
      end

      # Replace `$root` placeholder with actual environment root.
      def expand_root_path(path)
        path.to_s.sub(/^\$root/, @root)
      end

      # Replace actual environment root with `$root` placeholder.
      def relativize_root_path(path)
        path.to_s.sub(/^#{Regexp.escape(@root)}/, '$root')
      end

      # Check if dependency is fresh.
      #
      # `dep` is a `Hash` with `path`, `mtime` and `hexdigest` keys.
      #
      # A `Hash` is used rather than other `Asset` object because we
      # want to test non-asset files and directories.
      def dependency_fresh?(environment, dep)
        path, mtime, hexdigest = dep.pathname.to_s, dep.mtime, dep.digest

        stat = environment.stat(path)

        # If path no longer exists, its definitely stale.
        if stat.nil?
          return false
        end

        # Compare dependency mime to the actual mtime. If the
        # dependency mtime is newer than the actual mtime, the file
        # hasn't changed since we created this `Asset` instance.
        #
        # However, if the mtime is newer it doesn't mean the asset is
        # stale. Many deployment environments may recopy or recheckout
        # assets on each deploy. In this case the mtime would be the
        # time of deploy rather than modified time.
        if mtime >= stat.mtime
          return true
        end

        digest = environment.file_digest(path)

        # If the mtime is newer, do a full digest comparsion. Return
        # fresh if the digests match.
        if hexdigest == digest.hexdigest
          return true
        end

        # Otherwise, its stale.
        false
      end
  end
end


class BundledAsset < Asset
    attr_reader :source

    def initialize(environment, logical_path, pathname)
      super(environment, logical_path, pathname)

      @processed_asset = environment.find_asset(pathname, :bundle => false)
      @required_assets = @processed_asset.required_assets

      @source = ""

      # Explode Asset into parts and gather the dependency bodies
      to_a.each { |dependency| @source << dependency.to_s }

      # Run bundle processors on concatenated source
      context = environment.context_class.new(environment, logical_path, pathname)
      @source = context.evaluate(pathname, :data => @source,
                  :processors => environment.bundle_processors(content_type))

      @mtime  = to_a.map(&:mtime).max
      @length = Rack::Utils.bytesize(source)
      @digest = environment.digest.update(source).hexdigest
    end

    # Initialize `BundledAsset` from serialized `Hash`.
    def init_with(environment, coder)
      super

      @processed_asset = environment.find_asset(pathname, :bundle => false)
      @required_assets = @processed_asset.required_assets

      if @processed_asset.dependency_digest != coder['required_assets_digest']
        raise UnserializeError, "processed asset belongs to a stale environment"
      end

      @source = coder['source']
    end

    # Serialize custom attributes in `BundledAsset`.
    def encode_with(coder)
      super

      coder['source'] = source
      coder['required_assets_digest'] = @processed_asset.dependency_digest
    end

    # Get asset's own processed contents. Excludes any of its required
    # dependencies but does run any processors or engines on the
    # original file.
    def body
      @processed_asset.source
    end

    # Return an `Array` of `Asset` files that are declared dependencies.
    def dependencies
      to_a.reject { |a| a.eql?(@processed_asset) }
    end

    # Expand asset into an `Array` of parts.
    def to_a
      required_assets
    end

    # Checks if Asset is stale by comparing the actual mtime and
    # digest to the inmemory model.
    def fresh?(environment)
      @processed_asset.fresh?(environment)
    end
  end
end
