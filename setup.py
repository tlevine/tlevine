from distutils.core import setup

from tlevine import __version__

setup(name='tlevine',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Get links to Tom things.',
      url='https://github.com/tlevine/tlevine',
      packages=['tlevine'],
      scripts=['bin/tlevine'],
      install_requires = [
          'picklecache==0.0.3',
          'requests>==2.2.1'
      ],
      tests_require = ['nose'],
      version=__version__,
      license='AGPL',
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
      ],
)
