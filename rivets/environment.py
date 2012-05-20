from base import Base
from context import Context
from index import Index

import mime
import processing
import engines
import paths

import crawl
import logging

class Environment(Base):
    ''' `Environment` should initialized with your application's root
        directory. This should be the same as your Rails or Rack root.
        
             env = Environment.new(Rails.root)
    '''

    def __new__(self,root = ".",block=None):
      self.trail = crawl.Trail(root)

      self.logger = logging.getLogger()
      self.logger.setLevel(logging.CRITICAL)

      self.default_external_encoding = 'UTF-8'

      # Create a safe `Context` subclass to mutate
      self.context_class = type('ThisContext',(Context),{})()

      # Set MD5 as the default digest
      import hashlib
      self.digest_class = hashlib.md5
      self.version = ''

      self.mime_types        = mime.registered_mime_types
      self.engines           = engines.engines
      self.preprocessors     = processing.preprocessors
      self.postprocessors    = processing.postprocessors
      self.bundle_processors = processing.bundle_processors

      for path in paths.paths:
        append_path(path,self.trail)

      for ext,klass in self.engines.iteritems():
        processing.add_engine_to_trail(ext, klass)

      for ext,type in self.mime_types.iteritems():
        self.trail.append_extension(ext)

      self.expire_index()

      if block:
        return block()
      else:
        return self

    def index(self):
      ''' Returns a cached version of the environment.
          
          All its file system calls are cached which makes `index` much
          faster. This behavior is ideal in production since the file
          system only changes between deploys.
      '''
      return Index(self)

    def find_asset(self,path, options = {}):
      ''' Cache `find_asset` calls '''
      if not options.has_key('bundle'):
        options['bundle'] = True

      # Ensure inmemory cached assets are still fresh on every lookup
      asset = self.assets[cache_key_for(path, options)]
      if asset and asset.is_fresh(self):
        return asset
      else:
        asset = index.find_asset(path, options)
        if asset:
          # Cache is pushed upstream by Index#find_asset
          return asset

      def expire_index(self):
        # Clear digest to be recomputed
        self.digest = None
        self.assets = {}
