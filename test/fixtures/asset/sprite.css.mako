/*
 *= depend_on "POW.png"
 */

<%
  import base64,os
  path = os.path.realpath("test/fixtures/asset/POW.png")
  data = base64.b64encode(open(path,'rb').read())
%>
.pow {
  background: url(data:image/png;base64,${data}) no-repeat;
}
