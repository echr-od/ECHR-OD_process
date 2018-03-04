from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='NLP SEO',
    version='0.1.0',
    description='Natural Language Process for SEO',
    long_description=long_description,
    url='https://bitbucket.org/aquemy/nlp_seo',
    license='MIT',
    packages=['NLP'],
    install_requires=['numpy', 
            'scipy', 
            'gensim', 
            'nltk',
            'click',
            'unicodedata'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    scripts=['bin/download-nltk'],
    package_data = {
        'NLP': ['data/*.csv'],
    },
    zip_safe=False
)
