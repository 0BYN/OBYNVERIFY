from setuptools import setup, find_packages

setup(
    name="obyn-obyntemplate",
    version="0.1.0",
    description="An example plugin for ObynBot",
    packages=find_packages(),
    install_requires=[
        "disnake",
        "obynutils",
        "quart"
    ],
)