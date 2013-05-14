from setuptools import setup

version = '0.1dev'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'celery',
    'ddsc-logging',
    'psycopg2',
    'setuptools',
    ],

tests_require = [
    'coverage',
    'nose',
    ]

setup(name='ddsc-socket',
      version=version,
      description="Socket server that handles incoming sensor data",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python'],
      keywords=[],
      author='Shaoqing Lu',
      author_email='S.Lu@fugro.nl',
      url='https://github.com/ddsc/ddsc-socket',
      license='MIT',
      packages=['ddsc_socket'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ]},
      )
