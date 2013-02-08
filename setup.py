from distutils.core import setup

setup(name='Rivets',
	  version='0.2',
	  url='https://github.com/OiNutter/rivets',
	  download_url='https://github.com/OiNutter/rivets/tarball/master',
	  description='Python asset packaging system. Based on Sprockets ruby gem',
	  author='Will McKenzie',
	  author_email='will@oinutter.co.uk',
	  packages=['rivets'],
	  package_dir={'rivets': 'rivets'},
	  requires=['crawl(>=0.5.4)','lean(>=0.2.3)','uglipyjs','slimmer'],
	  license='MIT License',
	  classifiers=[
	  		'Development Status :: 3 - Alpha',
	  		'Environment :: Web Environment',
	  		'Intended Audience :: Developers',
	  		'License :: OSI Approved :: MIT License',
	  		'Programming Language :: Python :: 2',
        	'Programming Language :: Python :: 2.6',
        	'Programming Language :: Python :: 2.7',
        	'Programming Language :: JavaScript'
	  ]
)
