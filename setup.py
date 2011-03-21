import setuptools

setuptools.setup(
	name="OpenLegLib",
	version="0.1.0",
	license="MIT",
	
	author="Graylin Kim",
	author_email="graylin.kim@gmail.com",
	url="https://github.com/GraylinKim/Open",
	
	description="Library for the NY Senate Open Legislation Data Api",
	long_description=''.join(open("README.rst").readlines()),
	keywords=["starcraft 2","sc2","parser","replay"],
	classifiers=[
			"Environment :: Console",
			"Development Status :: 4 - Beta",
			"Programming Language :: Python",
			"Programming Language :: Python :: 2.7",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Natural Language :: English",
			"Operating System :: OS Independent",
			"Environment :: Other Environment",
			"Topic :: Utilities",
			"Topic :: Software Development :: Libraries",
		],
	
	requires=['decorator'],
	packages=['OpenLegLib'],
)
