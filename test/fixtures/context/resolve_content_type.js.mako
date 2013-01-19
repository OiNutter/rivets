${resolve("foo.js")},
${resolve("foo.js", content_type = "application/javascript")},
${resolve("foo.js", content_type = 'self')},
<% 
	try: 
		context.write(resolve("foo.js", content_type ="text/css"))
	except Exception,e:
		context.write(str(e))
%>