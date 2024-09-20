from setuptools import setup, find_packages

setup(
    name="obyn-obynverification",
    version="0.1.0",
    description="An verification plugin for ObynBot",
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="GizmoShiba",
    author_email="gizmoshiba@gmail.com",
    install_requires=[
        "disnake",
        "obynutils",
        "quart",
        "sqlalchemy"
    ],
)