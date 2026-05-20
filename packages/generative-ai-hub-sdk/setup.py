import sys
# To use a consistent encoding
from codecs import open  # pylint:disable=redefined-builtin
from collections import defaultdict
from glob import glob

from setuptools import setup, find_packages

VERSION_FILE = 'version.txt'
README_FILE = 'PYPIDESCRIPTION.md'
REQUIREMENTS_FILE = 'requirements.txt'

def get_version(version_file=VERSION_FILE):
    with open(version_file, encoding='utf-8-sig', mode='r') as ver_file:
        version_str = ver_file.readline().rstrip()
    return version_str

def get_readme(readme_file=README_FILE):
    with open(readme_file, encoding='utf-8-sig', mode='r') as readme_file:
        readme_list = [line.rstrip() for line in readme_file.readlines()]
    return readme_list

def get_install_requires(file_requirements=REQUIREMENTS_FILE, add_all=True, separator='#'):
    """
    Return a dictionary mapping extras (key) to set of requirements (value)
    """
    install_requires = set()
    with open(file_requirements, encoding='utf-8-sig', mode='r') as fp:
        extra_deps = defaultdict(set)
        for line in fp:
            line = line.strip()
            if line.startswith('#'):
                continue
            elif separator in line:
                tags = set()
                requirement, extra_tags = line.split(separator)
                requirement = requirement.rstrip()  # Remove additional spaces, if any
                # update set of tags
                tags.update(vv.strip() for vv in extra_tags.split(','))
                for t in tags:
                    extra_deps[t].add(requirement)
            elif len(line) > 0 and line[0].isalpha():
                install_requires.add(line.strip())
    if add_all:
        extra_deps['all'] = set(vv for v in extra_deps.values() for vv in v)
    extra_deps.update({k: list(v) for k, v in extra_deps.items()})
    return {
        'install_requires': [*install_requires],
        'extras_require': extra_deps,
    }

if len(sys.argv) > 1 and sys.argv[1] == '--get-dependencies':
    try:
        requested = sys.argv[2]
    except IndexError:
        requested = 'all'
    components = [s.strip() for s in requested.split(',') if len(s) > 0]
    requirements = get_install_requires()
    deps = set(requirements['install_requires'])
    extra_deps = requirements['extras_require']
    for comp in components:
        deps.update(extra_deps[comp])
    deps = sorted(set(deps))
    deps = [d.strip() for d in deps if all([not d.startswith(f) for f in ['sap-doxml-commons']])]
    print(' '.join(deps))
    sys.exit(0)


def generate_metadata():
    classifiers = """\
    Development Status :: 5 - Production/Stable
    Intended Audience :: Developers
    License :: Other/Proprietary License
    Operating System :: MacOS :: MacOS X
    Operating System :: Microsoft :: Windows :: Windows 10
    Operating System :: Microsoft :: Windows :: Windows 7
    Operating System :: Microsoft :: Windows :: Windows 8
    Operating System :: Microsoft :: Windows :: Windows 8.1
    Operating System :: Microsoft :: Windows :: Windows Server 2008
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
        summary="SDK for access to large language models in the Generative AI Hub",
        description="SAP Cloud SDK for AI (Python): generative AI SDK",
        long_description="\n".join(get_readme()),
        long_description_content_type='text/markdown',
        keywords="SAP AI Core, SAP generative AI SDK, SAP Generative AI Hub",
        url="https://www.sap.com/",
        author="SAP SE",
        download_url="https://pypi.python.org/pypi/sap-ai-sdk-gen",
        license='SAP DEVELOPER LICENSE AGREEMENT',
        classifiers=[_f for _f in classifiers.split('\n') if _f],
        platforms=["Windows", "Linux", "Mac OS-X", "Unix"],
        version=get_version(),
        packages=find_packages(exclude=['*test*']),
        python_requires='>=3.9',
        zip_safe=False,
        obsoletes_dist="generative-ai-hub-sdk"
    )
    return metadata

setup(
    name = "sap-ai-sdk-gen",
    include_package_data=True,
    data_files = [
        ('docs', glob('docs/*.html')),
    ],
    ** generate_metadata(),
    **get_install_requires(add_all=True)
)
