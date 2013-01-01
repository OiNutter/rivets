import re
from os import path

def normalize_extension(ext):
	ext = str(ext)
	if re.match(r"^\.",ext):
		return ext
	else:
		return ".%s" % ext

def get_extension(file):
	pattern = str(file).lower()
	
	ext = pattern
	while len(pattern):
		pattern = path.basename(pattern)
		ext = pattern
		pattern = re.sub(r'^[^.]*\.?','',pattern)

   	return ".%s" % ext