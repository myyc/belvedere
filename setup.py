from setuptools import setup

from belvedere import __version__

DESC = """
TBD
"""


setup(
    name="belvedere",
    version=__version__,
    author="myyc",
    description="Russian dolls code at its finest",
    license="BSD",
    keywords="data mining football python crawler",
    packages=["belvedere"],
    long_description=DESC,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=["cherrypy", "jinja2", "selenium", "redis"],
)
