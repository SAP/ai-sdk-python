"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from codecs import open  # pylint:disable=redefined-builtin
from glob import glob

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

VERSION_FILE = 'version.txt'
README_FILE = 'PYPIDESCRIPTION.md'


def get_version():
    with open(VERSION_FILE) as ver_file:
        version_str = ver_file.readline().rstrip()
    return version_str


def get_readme():
    with open(README_FILE) as readme_file:
        readme_list = [line.rstrip() for line in readme_file.readlines()]
    return readme_list


def get_install_requires():
    with open('requirements.txt') as reqs_file:
        reqs = [line.rstrip() for line in reqs_file.readlines()]
    return reqs


def generate_metadata():
    classifiers = """\
    Development Status :: 5 - Production/Stable
    Intended Audience :: Developers
    License :: Other/Proprietary License
    Operating System :: MacOS
    Operating System :: Microsoft :: Windows
    Operating System :: POSIX :: Linux
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: 3.11
    Programming Language :: Python :: 3.12
    Programming Language :: Python :: 3.13
    Programming Language :: Python :: 3.14
    Topic :: Software Development :: Libraries :: Python Modules"""
    metadata = dict(
        description="SAP Cloud SDK for AI (Python): Base Client",
        long_description="\n".join(get_readme()),
        long_description_content_type='text/markdown',
        keywords="SAP AI Core",
        url="https://www.sap.com/",
        author="SAP SE",
        download_url="https://pypi.python.org/pypi/ai-api-client-sdk",
        license='SAP DEVELOPER LICENSE AGREEMENT',
        classifiers=[_f for _f in classifiers.split('\n') if _f],
        platforms=["Windows", "Linux", "Mac OS-X", "Unix"],
        version=get_version(),
        packages=find_packages(exclude=['*test*']),
        python_requires='>=3.9',
        zip_safe=False,
        obsoletes_dist="ai-api-client-sdk",
    )
    return metadata


setup(name="sap-ai-sdk-base",
      include_package_data=True,
      install_requires=get_install_requires(),
      data_files=[
        ('docs', glob('docs/*.html')),
      ],
      **generate_metadata()
      )
