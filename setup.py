from distutils.core import setup, Extension
from Cython.Build import cythonize
from numpy import get_include # cimport numpy を使うため

ext = Extension("cdefinitions", sources=["cdefinitions.pyx"], include_dirs=['.', get_include()])
setup(name="cdefinitions", ext_modules=cythonize([ext]))
