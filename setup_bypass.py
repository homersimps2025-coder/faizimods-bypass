from setuptools import setup
from Cython.Build import cythonize

setup(
    name="bypass",
    ext_modules=cythonize(
        "bypass.pyx",
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
        }
    )
)
