"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open  # pylint:disable=redefined-builtin
from glob import glob



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
    License :: Other/Proprietary License
    Operating System :: MacOS :: MacOS X
    Operating System :: Microsoft :: Windows
    Operating System :: POSIX :: Linux
    Intended Audience :: Developers
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: 3.11
    Programming Language :: Python :: 3.12
    Programming Language :: Python :: 3.13
    Programming Language :: Python :: 3.14
    Topic :: Software Development :: Libraries :: Python Modules"""
    metadata = dict(
        summary="SDK for SAP AI Core APIs",
        description="SAP Cloud SDK for AI (Python): Core SDK",
        long_description="\n".join(get_readme()),
        long_description_content_type='text/markdown',
        keywords="SAP AI Core, SAP AI Core API",
        url="https://www.sap.com/",
        author="SAP SE",
        download_url="https://pypi.python.org/pypi/ai-core-sdk",
        license='SAP DEVELOPER LICENSE AGREEMENT',
        classifiers=[_f for _f in classifiers.split('\n') if _f],
        platforms=["Windows", "Linux", "Mac OS-X", "Unix"],
        version=get_version(),
        packages=find_packages(exclude=['*test*']),
        python_requires='>=3.9',
        zip_safe=False,
        obsoletes_dist="ai-core-sdk",
    )
    return metadata


setup(name="sap-ai-sdk-core",
      include_package_data=True,
      install_requires=get_install_requires(),
      data_files=[
        ('docs', glob('docs/*.html')),
      ],
      entry_points={
          'console_scripts': [
              'aicore=ai_core_sdk.cli:cli',
          ],
      },
      **generate_metadata()
      )
