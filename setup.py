from setuptools import setup, find_packages

setup(
    name="teams-core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mesa",
        "solara",
        "matplotlib",
    ],
)
