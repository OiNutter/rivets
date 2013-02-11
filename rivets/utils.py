import codecs
import re

UTF8_BOM_PATTERN = re.compile("\\A(\\xFE\\xFF|\\xFF\\xFE)".encode('utf-8'))

def read_unicode(filename,external_encoding='utf8'):
	data = codecs.open(filename,encoding=external_encoding).read()

	if UTF8_BOM_PATTERN.match(data):
		return unicode(UTF8_BOM_PATTERN.sub('',data)).encode('utf8')
	else:
		return unicode(data).encode('utf8')

def unique_list(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if x not in seen and not seen_add(x)]