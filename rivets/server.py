import cherrypy
import regex as re
from urllib import unquote_plus
import traceback
from wsgiref.handlers import format_date_time

class Server(object):

	def run(self,path,**kwargs):

		path = unquote_plus(path).encode('utf8')

		try:

			if self.is_forbidden_request(path):
				return self.forbidden_response()

			fingerprint = self.path_fingerprint(path)
			if fingerprint:
				path = re.sub("-%s"%fingerprint,'',path)

			# Look up the asset
			asset = self.find_asset(path,bundle= not self.is_body_only())

			if not asset:
				return self.not_found_response()
			elif self.etag_match(asset):
				return self.not_modified_response(asset)
			else:
				return self.ok_response(asset)

		except cherrypy.HTTPError:
			raise
		except Exception,e:
			content_type = self.get_content_type_of(path)
			if content_type == 'application/javascript':
				return self.javascript_exception_response(e)
			elif content_type == 'text/css':
				return self.css_exception_response(e)
			else:
				raise

	def is_forbidden_request(self,path):
		''' Prevent access to files elsewhere on the file system
        
             http://example.org/assets/../../../etc/passwd
        '''
		return '..' in path

	def forbidden_response(self):
		cherrypy.response.headers['Content-Type']='text/plain'
		cherrypy.response.headers['Content-Length']='9'
		raise cherrypy.HTTPError(403,'Forbidden')

	def not_found_response(self):
		cherrypy.response.headers['Content-Type']='text/plain'
		cherrypy.response.headers['Content-Length']='9'
		cherrypy.response.headers['X-Cascade']='pass'
		raise cherrypy.NotFound()

	def javascript_exception_response(self,e):
		err = "%s: %s" % (e.__class__.__name__,str(e))
		body = 'throw Error("%s")' % err

		cherrypy.response.headers['Content-Type']='application/javascript'
		cherrypy.response.headers['Content-Length']=len(body)
		return body

	def css_exception_response(self,e):
		message = "\n%s: %s" % (e.__class__.__name__,traceback.format_exc())
		backtrace = "\n %s" % traceback.format_stack()[0]

		body = '''
html {
	padding: 18px 36px;
}

head {
	display: block;
}

body {
	margin: 0;
	padding: 0;
}

body > * {
	display: none !important;
}

head:after, body:before, body:after{
	display: block !important;
}

head:after{
	font-family: sans-serif;
	font-size: large;
	font-weight: bold;
	content: "Error compiling CSS asset";
}

body:before, body:after {
	font-family: monospace;
	white-space: pre-wrap;
}

body:before {
	font-weight:bold'
	content: "%s"
}

body:after {
	content: "%s"
}
''' % (self.escape_css_content(message),self.escape_css_content(backtrace))
		cherrypy.response.headers['Content-Type']='text/css;charset=utf-8'
		cherrypy.response.headers['Content-Length']=len(body)
		return body

	def escape_css_content(self,content):
		content = re.sub(r"""\\""",r"""\\005c""",content)
		content = re.sub(r"""\\n""",r"""\\000a""",content)
		content = re.sub('"',"\\\\0022",content)
		content = re.sub('/','\\\\002f',content)
		return content

	def etag_match(self,asset):
		return cherrypy.request.headers.get('Http-If-None-Match',None) == self.etag(asset)

	def is_body_only(self):
		return cherrypy.request.params.get('body',False) and cherrypy.request.params.get('body',False) != 'false'

	def not_modified_response(self,asset):
		cherrypy.response.headers['Content-Type']=None
		cherrypy.response.headers['Content-Length']=None
		cherrypy.response.headers['Last-Modified']=None
		cherrypy.response.status = 304

	def ok_response(self,asset):
		self.headers(asset,asset.length)
		return str(asset)

	def headers(self,asset,length):
		cherrypy.response.headers['Content-Type']=asset.content_type
		cherrypy.response.headers['Content-Length']=str(length)

		cherrypy.response.headers['Cache-Control']='public'
		cherrypy.response.headers['Last-Modified']=format_date_time(asset.mtime)
		cherrypy.response.headers["ETag"] = self.etag(asset)

		if self.path_fingerprint(cherrypy.request.path_info):
			cherrypy.response.headers["Cache-Control"] += ", max-age=31536000"
		else:
			cherrypy.response.headers["Cache-Control"] += ", must-revalidate"

	def path_fingerprint(self,path):
		matches = re.findall(r"""-([0-9a-f]{7,40})\.[^.]+$""",path)
		return matches[0] if matches else None

	def etag(self,asset):
		return '"%s"' % asset.digest
