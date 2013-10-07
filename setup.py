from setuptools import setup

setup(name='Rivets',
	  version='0.4.1',
	  url='https://github.com/OiNutter/rivets',
	  download_url='https://github.com/OiNutter/rivets/tarball/master',
	  description='Python asset packaging system. Based on Sprockets ruby gem',
	  author='Will McKenzie',
	  author_email='will@oinutter.co.uk',
	  packages=['rivets'],
	  include_package_data=True,
	  package_data={'rivets': ['rivets/*.py','rivets/assets/*.py']},
	  install_requires=['crawl>=0.5.5','lean>=0.2.3','cherrypy','regex'],
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
