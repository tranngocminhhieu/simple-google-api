from pathlib import Path
from setuptools import setup

README = (Path(__file__).parent / "README.md").read_text()

setup(
    name='simplegoogleapi',
    version='0.1.2',
    description='A simple way to work with Google API',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/tranngocminhhieu/simple-google-api',
    author='Tran Ngoc Minh Hieu',
    author_email='tnmhieu@gmail.com',
    packages=['simplegoogleapi'],
    package_data={'simplegoogleapi': ['auth/*', 'drive/*']},
    install_requires=[
        'requests',
        'pydrive2',
        'google-api-python-client',
        'oauth2client',
        'httplib2'
    ]
)