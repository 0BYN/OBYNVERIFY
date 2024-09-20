from setuptools import setup, find_packages

setup(
    name="obyn-obynverification",
    version="0.1.0",
    description="An verification plugin for ObynBot",
    packages=find_packages(),
    install_requires=[
        "disnake",
        "obynutils",
        "quart",
        "sqlalchemy"
    ],
)