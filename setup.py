from distutils.core import setup
import setuptools

setup(
    name='pycscl',
    version='0.3.0-dev',
    author='Felix Kutzner',
    author_email='felixkutzner@gmail.com',
    url='https://github.com/fkutzner/PyCSCL',
    license='MIT',
    description='Lightweight SAT Boolean constraint encoder library',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages()
)
