from registry import MimeTypeRegistry

mimetype_registry = MimeTypeRegistry()

mimetype_registry.register_mimetype('.js','application/javascript')
mimetype_registry.register_mimetype('.css','text/css')