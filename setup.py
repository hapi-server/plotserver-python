from setuptools import setup, find_packages
import sys

#"hapiplot @ git+https://github.com/hapi-server/plot-python@main#egg=hapiplot",
#"hapiclient @ git+https://github.com/hapi-server/client-python@master#egg=hapiclient"
install_requires = ["hapiclient",
                    "hapiplot",
                    "Flask==1.0.2",
                    "gunicorn==19.9.0",
                    "python-slugify",
                    "requests",
                    "Pillow"]

if len(sys.argv) > 1 and sys.argv[1] == 'develop':
    install_requires.append("Pillow")
    install_requires.append("requests")

# version is modified by misc/version.py. See Makefile.
setup(
    name='hapiplotserver',
    version='0.0.7b1',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/hapiplotserver/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    include_package_data=True,
    scripts=["hapiplotserver/hapiplotserver"] 
)

























































