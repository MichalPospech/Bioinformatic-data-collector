from setuptools import setup, find_packages

setup(
    name="BioinformaticDataCollector",
    version="0.0.1",
    description="Bioinformatic data collector",
    author="Michal Pospech",
    author_email="michal.pospech@gmail.com",
    url="https://www.python.org/sigs/distutils-sig/",
    packages=find_packages(include=["lib"]),
)
