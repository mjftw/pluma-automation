import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="farm-core",
    version="0.0.1",
    author="Merlin Webster",
    author_email="mwebster@witekio.com",
    description="Automation Lab: farm-core",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/adeneo-embedded/farm-core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
