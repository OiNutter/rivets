import re

def normalize_extension(ext):
	ext = str(ext)
	if not re.search(r"^\."):
		return ext
	else:
		return ".%s" % ext
