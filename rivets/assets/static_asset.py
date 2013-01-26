import os

from asset import Asset

class StaticAsset(Asset):
	
	@property
	def source(self):
		return open(self.pathname,'r+').read()

	def to_path(self):
		return self.pathname

	def write_to(self,filename,**options):

		try:
			import shutil

			if not options.has_key('compress'):
				name,ext = os.path.splitext(filename)
				options['compress'] = ext == '.gz'

			dirname = os.path.dirname(filename)
			if not os.path.exists(dirname):
				os.makedirs(dirname)

			if options['compress']:
				import gzip
				a = open(self.pathname,'rb')
				f = gzip.open('%s+'%filename,'wb')
				buf = ""
				while True:
					buf=a.read(16384)
					if buf:
						f.write(buf)
					else:
						break
				f.close()
				os.utime('%s+'%filename,(self.mtime,self.mtime))
			else:
				shutil.copy(self.pathname,'%s+'%filename)

			shutil.move("%s+"%filename,filename)

			os.utime(filename,(self.mtime,self.mtime))

		finally:
			if os.path.exists("%s+"%filename):
				os.remove("%s+"%filename)
