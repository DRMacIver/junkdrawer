import os

import setuptools


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


SOURCE = local_file("src")
README = local_file("README.md")

setuptools.setup(
    name="DRMacIver-junkdrawer",
    # Not actually published on pypi
    version="0.0.0",
    author="David R. MacIver",
    author_email="david@drmaciver.com",
    packages=setuptools.find_packages(SOURCE),
    package_dir={"": SOURCE},
    url=("https://github.com/DRMacIver/junkdrawer/"),
    license="MPL v2",
    description="",
    zip_safe=False,
    install_requires=[],
    long_description=open(README).read(),
)
