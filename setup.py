from setuptools import setup, find_packages
import sys

#"hapiplot @ git+https://github.com/hapi-server/plot-python@main#egg=hapiplot",
#"hapiclient @ git+https://github.com/hapi-server/client-python@master#egg=hapiclient"

# See 
# https://itsmycode.com/importerror-cannot-import-name-json-from-itsdangerous/
# for motivation for setting version for markupsafe (which is not used by
# hapiplotervers) here.
install_requires = ["hapiclient",
                    "hapiplot",
                    "isodate",
                    "markupsafe==2.0.1",
                    "Flask==1.1.4",
                    "gunicorn==19.9.0",
                    "requests==2.27.1",
                    "python-slugify",
                    "Pillow"]

if sys.version_info <= (3, 7):
    install_requires.insert(0,'numpy<=1.19')
    install_requires.insert(0,'matplotlib<3.4')

if len(sys.argv) > 1 and sys.argv[1] == 'develop':
    install_requires.append("Pillow")
    install_requires.append("requests")

# version is modified by misc/version.py. See Makefile.
setup(
    name='hapiplotserver',
    version='0.1.1',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/hapiplotserver/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    include_package_data=True,
    scripts=["hapiplotserver/hapiplotserver"] 
)

























































