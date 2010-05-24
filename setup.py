from setuptools import setup, find_packages

setup(
    name = "musicquiz",
    version = "0.0",
    url = 'http://github.com/mariusd/musicquiz',
    license = 'BSD',
    description = "",
    author = 'Marius Damarackas',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)
