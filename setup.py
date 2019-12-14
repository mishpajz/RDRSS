from setuptools import setup

setup(
    name='RDRSS',
    version='0.1',
    author='Michal Dobes',
    scripts=['rdrss/RDRSS.py'],
    install_requires=[
          'requests',
          'feedparser',
          'argparse',
      ],
    license='MIT',
    long_description=open('README.md').read(),
)
