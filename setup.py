"""
Setup of the dukaonesdk module
"""
from setuptools import setup

setup(
    name="dukaonesdk",
    version="1.0.2",
    description="Duka One ventilation SDK",
    long_description=(
        "SDK for connection to the Duka One S6W ventilation. "
        "Made for interfacing to home assistant"
    ),
    author="Jens Østergaard Nielsen",
    url="https://github.com/dingusdk/dukaonesdk",
    packages=["dukaonesdk"],
    license="GPL-3.0",
)
