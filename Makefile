# Development:
# Test repository code:
#   make repository-test     # Test using $(PYTHON)
#   make repository-test-all # Test on all versions in $(PYTHONVERS)
#
# Making a local package:
# 1. Update CHANGES.txt to have a new version line
# 2. make package
# 3. make package-test-all
#
# Upload package to pypi.org test starting with uploaded package:
# 1. make release
# 2. Wait ~5 minutes and execute
# 3. make release-test-all
#    (Will fail until new version is available at pypi.org for pip install.
#     Sometimes takes ~5 minutes even though web page is immediately
#     updated.)
# 4. After package is finalized, create new version number in CHANGES.txt ending
#    with "b0" in setup.py and then run
#       make version-update
# 	git commit -a -m "Update version for next release"
#    This will update the version information in the repository to indicate it
#    is now in a pre-release state.

PACKAGE_NAME=hapiplotserver

# Default Python version to use for tests
PYTHON=python3.7
PYTHON_VER=$(subst python,,$(PYTHON))

# Python versions to test
# TODO: Use tox.
PYTHONVERS=python3.8 python3.7 python3.6

# VERSION is updated in "make version-update" step and derived
# from CHANGES.txt. Do not edit.
VERSION=0.1.4
SHELL:= /bin/bash

LONG_TESTS=false

# Location to install Anaconda. Important: This directory is removed when
# make test is executed.
CONDA=anaconda3

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
  # CONDA=/c/tools/anaconda3
	CONDA=/c/tools/miniconda3
endif

CONDA_ACTIVATE=source $(CONDA)/etc/profile.d/conda.sh; conda activate

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	CONDA_ACTIVATE=source $(CONDA)/Scripts/activate; conda activate
endif


URL=https://upload.pypi.org/
REP=pypi

pythonw=$(PYTHON)

# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	pythonw=python
endif

ifeq ($(UNAME_S),Darwin)
	# Use pythonw instead of python. On OS-X, this prevents "need to install
	# python as a framework" error. The following finds the path to the binary
	# of $(PYTHON) and replaces it with pythonw, e.g., 
	# /opt/anaconda3/envs/python3.6/bin/python3.6
	# -> 
	# /opt/anaconda3/envs/python3.6/bin/pythonw
	a=$(shell source activate $(PYTHON); which $(PYTHON))
	pythonw=$(subst bin/$(PYTHON),bin/pythonw,$(a))
endif

################################################################################
# Test contents in repository using different python versions
.PHONY: test
test:
	make repository-test-all

repository-test-all:
	- rm -rf $(CONDA)
	@ for version in $(PYTHONVERS) ; do \
		make repository-test PYTHON=$$version ; \
	done

# These require visual inspection.
repository-test:
	@make clean
	- conda remove --name $(PYTHON) --all -y
	make condaenv PYTHON=$(PYTHON)
	pip uninstall -y hapiclient hapiplot hapiplotserver
	$(CONDA_ACTIVATE) $(PYTHON); $(PYTHON) setup.py develop | grep "Best"
	#$(CONDA_ACTIVATE) $(PYTHON); pip install pytest
	$(CONDA_ACTIVATE) $(PYTHON); pip install --no-cache-dir -e .
	bash hapiplotserver/test/test_hapiplotserver.sh
	$(CONDA_ACTIVATE) $(PYTHON) && $(PYTHON) hapiplotserver/test/test_commandline.py

repository-test-other:
	$(CONDA_ACTIVATE) $(PYTHON) && $(PYTHON) hapiplotserver/test/test_hapiplotserver.py

################################################################################

################################################################################
# Anaconda
CONDA_PKG=Miniconda3-latest-Linux-x86_64.sh
ifeq ($(shell uname -s),Darwin)
	CONDA_PKG=Miniconda3-latest-MacOSX-x86_64.sh
endif

condaenv:
# ifeq ($(shell uname -s),MINGW64_NT-10.0-18362)
ifeq ($(TRAVIS_OS_NAME),windows)
	cp $(CONDA)/Library/bin/libcrypto-1_1-x64.* $(CONDA)/DLLs/
	cp $(CONDA)/Library/bin/libssl-1_1-x64.* $(CONDA)/DLLs/
	$(CONDA)/Scripts/conda create -y --name $(PYTHON) python=$(PYTHON_VER)
else
	make $(CONDA)/envs/$(PYTHON) PYTHON=$(PYTHON)
endif

$(CONDA)/envs/$(PYTHON): $(CONDA)
	$(CONDA_ACTIVATE); \
		$(CONDA)/bin/conda create -y --name $(PYTHON) python=$(PYTHON_VER)

$(CONDA): /tmp/$(CONDA_PKG)
	bash /tmp/$(CONDA_PKG) -u -b -p $(CONDA)

/tmp/$(CONDA_PKG):
	curl https://repo.anaconda.com/miniconda/$(CONDA_PKG) > /tmp/$(CONDA_PKG) 
################################################################################

################################################################################
venv-test:
	source env-$(PYTHON)/bin/activate && \
		pip uninstall -y hapiclient hapiplot hapiplotserver && \
		pip install --no-cache-dir --pre '$(PACKAGE)' \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple && \
		env-$(PYTHON)/bin/python hapiplotserver/test/test_commandline.py && \
		env-$(PYTHON)/bin/python hapiplotserver/test/test_commandline.py
################################################################################

################################################################################
# Packaging
package:
	make clean
	make version-update
	python setup.py sdist

package-test-all:
	@ for version in $(PYTHONVERS) ; do \
		make repository-test PYTHON=$$version ; \
	done

env-$(PYTHON):
	$(CONDA_ACTIVATE) $(PYTHON); \
		conda install -y virtualenv; \
		$(PYTHON) -m virtualenv env-$(PYTHON)

package-test:
	make package
	make env-$(PYTHON)
	make venv-test PACKAGE='dist/$(PACKAGE_NAME)-$(VERSION).tar.gz'
################################################################################

################################################################################
release:
	make package
	make version-tag
	make release-upload

release-upload:
	pip install twine
	echo "rweigel, t1p"
	twine upload \
		-r $(REP) dist/$(PACKAGE_NAME)-$(VERSION).tar.gz \
		&& echo Uploaded to $(subst upload.,,$(URL))/project/$(PACKAGE_NAME)/

release-test-all:
	@ for version in $(PYTHONVERS) ; do \
		make release-test PYTHON=$$version ; \
	done

release-test:
	rm -rf env
	$(CONDA_ACTIVATE) $(PYTHON); pip install virtualenv; $(PYTHON) -m virtualenv env
	make venv-test PACKAGE='$(PACKAGE_NAME)==$(VERSION)'
################################################################################

################################################################################
# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py

version-tag:
	git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags
################################################################################

################################################################################
# Install package in local directory (symlinks made to local dir)
install-local:
	#python setup.py -e .
	$(CONDA_ACTIVATE) $(PYTHON); pip install --editable .

install:
	pip install '$(PACKAGE_NAME)==$(VERSION)' --index-url $(URL)/simple
	conda list | grep $(PACKAGE_NAME)
	pip list | grep $(PACKAGE_NAME)
################################################################################

clean:
	- @find . -name __pycache__ | xargs rm -rf {}
	- @find . -name *.pyc | xargs rm -rf {}
	- @find . -name *.DS_Store | xargs rm -rf {}
	- @find . -type d -name __pycache__ | xargs rm -rf {}
	- @find . -name *.pyc | xargs rm -rf {}
	- @rm -f *~
	- @rm -f \#*\#
	- @rm -rf env
	- @rm -rf dist
	- @rm -f MANIFEST
	- @rm -rf .pytest_cache/
	- @rm -rf $(PACKAGE_NAME).egg-info/
