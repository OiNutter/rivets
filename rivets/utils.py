import io

def read_unicode(filename):
	data = io.open(filename).read()
	data = unicode(data,'utf8')
	data = data.replace('\t',' ')

	return data

def unique_list(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if x not in seen and not seen_add(x)]