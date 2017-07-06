try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Extracts transactions of the last week and imports them into the new YNAB',
    'author': 'Johannes Rueschel',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'code+ynab@rueschel.de',
    'version': '0.1',
    'install_requires': ['nose', 'pynYNAB'],
    'packages': ['m2ynab'],
    'scripts': [],
    'name': 'm2ynab'
}

setup(**config)
