from distutils.core import setup

setup(name='Rivets',
	  version='0.2',
	  description='Python asset packaging system. Based on Sprockets ruby gem',
	  author='Will McKenzie',
	  author_email='will@oinutter.co.uk',
	  packages=['rivets'],
	  package_dir={'rivets': 'rivets'},
	  requires=['crawl','lean','uglipyjs','slimmer']
	  )
