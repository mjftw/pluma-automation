import setuptools


readme_file = "readme.md"
try:
    with open(readme_file, "r") as fh:
        long_description = fh.read()
        long_description_content_type = "text/markdown"
except FileNotFoundError:
    print('Cannot find readme {}. Omitting long package description'.format(
        readme_file))
    long_description = None
    long_description_content_type = None

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
    install_requires=[
        'pyserial',
        'setuptools',
        'pyudev',
        'pexpect>=4.6',
        'pyftdi',
        'pyroute2',
        'pandas',
        'pygal',
        'cairosvg',
        'graphviz',
        'nanocom',
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha"
    ],
)
