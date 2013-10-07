import json
import os
import binascii
import datetime
import regex as re

from base import Base
from assets import BundledAsset

class Manifest(object):

	def __init__(self,environment=None,directory=None,path=None,*args,**kwargs):

		self.environment = environment

		self.dir = os.path.realpath(directory) if directory else None
		self.path = os.path.realpath(path) if path else None

		if not self.dir and self.path:
			self.dir = os.path.dirname(self.path)

		if self.dir and not self.path:

			paths = os.listdir(self.dir)
			paths = [path for path in paths if re.match(r"""manifest*.json""",os.path.basename(path))]

			if paths:
				self.path = paths[0]
			else:
				self.path = os.path.join(self.dir,"manifest-%s.json"%binascii.b2a_hex(os.urandom(8)))


		if not self.dir and not self.path:
			raise Exception('Manifest requries output path')

		data = None

		if os.path.exists(self.path):
			data = json.loads(open(self.path,'r+').read())
		
		self.data = data if isinstance(data,dict) else {}

	def assets(self):
		return self.data['assets'] if self.data.has_key('assets') else {}

	def files(self):
		return self.data['files'] if self.data.has_key('files') else {}


	def compile(self,*args):

		if not self.environment:
			raise Exception('Manifest requires environment for compilation')

		paths = list(self.environment.each_logical_path(*args)) + [path for path in args if os.path.isabs(path)]

		def build_manifest(path):
			asset = self.find_asset(path)
			files = self.files()
			assets = self.assets()
			if asset:
				files[asset.digest_path] = {
					'logical_path':asset.logical_path,
					'mtime': asset.mtime,
					'size': asset.length,
					'digest':asset.digest
				}

				assets[asset.logical_path] = asset.digest_path

				target = os.path.join(self.dir,asset.digest_path)

				if os.path.exists(target):
					print "Skipping %s, already exists" % target
				else:
					print "Writing %s" % target
					asset.write_to(target)
					if isinstance(asset,BundledAsset):
						asset.write_to("%s.gz"%target)

			self.save()
			return asset

		for path in paths:
			build_manifest(path)

	def remove(self,filename):
		path = os.path.join(self.dir,filename)
		gzip = "%s.gz" % path
		logical_path = self.files()[filename]['logical_path']
		assets = self.assets()
		files = self.files()

		if assets[logical_path] == filename:
			del assets[logical_path]

		del files[filename]

		if os.path.exists(path):
			os.remove(path)

		if os.path.exists(gzip):
			os.remove(gzip)

		self.save()

		print "Removed %s" % filename

	def clean(self,keep=2):
		for logical_path in self.assets().iterkeys():
			assets = self.backups_for(logical_path)

			assets = assets[keep:-1] if assets else []

			for asset in assets:
				self.remove(asset[0])

	def clobber(self):
		if os.path.exists(self.dir):
			os.rmdir(self.dir)
			print "Removed %s" % self.dir

	def backups_for(self,logical_path):
		files = self.files()
		assets = self.assets()

		backups = {}
		for filename,attrs in files.iteritems():
			if attrs['logical_path'] != logical_path and assets[logical_path] != filename:
				backups.append((filename,attrs))

		backups = sorted(backups,key=lambda x: datetime.datetime.fromtimestamp(x[1]['mtime']))

		backups.reverse()

		return backups


	def find_asset(self,logical_path):
		return self.environment.find_asset(logical_path)

	def save(self):
		if not os.path.exists(self.dir):
				os.makedirs(self.dir)

		with open(self.path,'w+') as f:
			f.write(json.dumps(self.data))