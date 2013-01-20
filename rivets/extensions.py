import regex as re
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

def get_output_extension(file):
	pattern = str(file).lower()

	full_ext = re.findall(r'(\..+)+$',pattern)

	if full_ext:
		full_ext.reverse()
		full_ext = full_ext[0]

		exts = re.findall(r'\.[^.]*',full_ext)
		exts.reverse()
		return exts[1] if len(exts) > 1 else exts[0]

	return ''


