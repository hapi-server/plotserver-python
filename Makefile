# Development: Test repository contents:
#   make test-repository
#
# Make and test a candidate release package in virtual environment:
# 1. Update CHANGES.txt to have a new version line
# 2. make package
#
# Make release package, upload to pypi.org, and test package
# 1. make release
# 2. Wait ~5 minutes and execute
# 3. make test-release
#    (Will fail until new version is available at pypi.org for pip install.
#     Sometimes takes ~5 minutes even though web page is immediately
#     updated.)
# 4. After package is finalized, create new version number in CHANGES.txt ending
#    with "bN" in setup.py and then run
#    make version-update.

PYTHON=python3.6
PYTHON_VER=$(subst python,,$(PYTHON))

# Select this to have anaconda installed 
CONDA=./anaconda3
# or using an existing installation
#CONDA=/opt/anaconda3
#CONDA=~/anaconda3
CONDA_ACTIVATE=source $(CONDA)/etc/profile.d/conda.sh; conda activate

# If CONDA not found, this package will be used and installed in ./anaconda3
CONDA_PKG=Miniconda3-latest-Linux-x86_64.sh
ifeq ($(shell uname -s),Darwin)
	CONDA_PKG=Miniconda3-latest-MacOSX-x86_64.sh
endif

URL=https://upload.pypi.org
REP=pypi

# VERSION below is updated in "make version-update" step.
VERSION=0.0.7b0
SHELL:= /bin/bash

CONDA=./anaconda3
#CONDA=/opt/anaconda3
#CONDA=~/anaconda3
CONDA_ACTIVATE=source $(CONDA)/etc/profile.d/conda.sh; conda activate

test:
    make test-virtualenv PYTHON=python3.6
    make test-virtualenv PYTHON=python2.7
	make test-repository PYTHON=python3.6
    make test-repository PYTHON=python2.7

test-repository:
	- rm -rf $(TMPDIR)/hapi-data
	make condaenv python=$(PYTHON)
	$(CONDA_ACTIVATE) $(PYTHON) && pip uninstall -y -q hapiplotserver
	$(CONDA_ACTIVATE) $(PYTHON) && pip install hapiclient
	$(CONDA_ACTIVATE) $(PYTHON) && $(PYTHON) setup.py develop | grep "Best"
	$(CONDA_ACTIVATE) $(PYTHON) && $(PYTHON) hapiplotserver/test/test_commandline.py
	$(CONDA_ACTIVATE) $(PYTHON) && $(PYTHON) hapiplotserver/test/test_hapiplotserver.py

test-virtualenv:
	rm -rf env
	$(CONDA_ACTIVATE) && pip install virtualenv && $(PYTHON) -m virtualenv env
	source env/bin/activate && \
	    pip install pytest requests Pillow && \
        pip install . && \
        pip install ../client-python
	source env/bin/activate && \
	    python hapiplotserver/test/test_commandline.py

#	source env/bin/activate && \
#	    python hapiplotserver/test/test_hapiplotserver.py
# does not work in virtualenv on OS-X. Logs show
# hapi(): Reading http://hapi-server.org/servers/TestData/hapi/info?id=dataset1
# ('Connection aborted.', RemoteDisconnected('Remote end closed connection
# without response',)). This happens even though the test works in the
# test-repository target.

conda:
	make $(CONDA) PYTHON=$(PYTHON)

condaenv: $(CONDA)
	make $(CONDA)/envs/$(PYTHON) PYTHON=$(PYTHON)

$(CONDA): /tmp/$(CONDA_PKG)
	bash /tmp/$(CONDA_PKG) -b -p $(CONDA)

/tmp/$(CONDA_PKG):
	curl https://repo.anaconda.com/miniconda/$(CONDA_PKG) > /tmp/$(CONDA_PKG) 

$(CONDA)/envs/$(PYTHON): $(CONDA)
	$(CONDA_ACTIVATE); \
		$(CONDA)/bin/conda create -y --name $(PYTHON) python=$(PYTHON_VER)

CONDA_PKG=Miniconda3-latest-Linux-x86_64.sh
ifeq ($(shell uname -s),Darwin)
	CONDA_PKG=Miniconda3-latest-MacOSX-x86_64.sh
endif

condaenv: 
	make $(CONDA)/envs/$(PYTHON) PYTHON=$(PYTHON)

$(CONDA)/envs/$(PYTHON): $(CONDA)
	$(CONDA_ACTIVATE); \
		$(CONDA)/bin/conda create -y --name $(PYTHON) python=$(PYTHON_VER)

$(CONDA): /tmp/$(CONDA_PKG)
	bash /tmp/$(CONDA_PKG) -b -p $(CONDA)

/tmp/$(CONDA_PKG):
	curl https://repo.anaconda.com/miniconda/$(CONDA_PKG) > /tmp/$(CONDA_PKG) 

package:
	make clean
	make version-update
	python setup.py sdist
	#make test-package PYTHON=python3.6
	#make test-package PYTHON=python2.7

test-package:
	rm -rf env
	$(PYTHON) -m virtualenv env
	source env/bin/activate && \
		pip install pytest && \
		pip install dist/hapiplotserver-$(VERSION).tar.gz \
			--index-url $(URL)/simple \
			--extra-index-url https://pypi.org/simple
	source env/bin/activate && \
	    bash hapiplotserver/test/test_hapiplotserver.sh
	source env/bin/activate && \
	    python hapiplotserver/test/test_hapiplotserver.py

test-release:
	rm -rf env
	python3 -m virtualenv env
	source env/bin/activate && \
		pip install pytest && \
		pip install 'hapiplotserver==$(VERSION)' \
			--index-url $(URL)/simple  \
			--extra-index-url https://pypi.org/simple 

release:
	make package
	make version-tag
	make release-upload

release-upload:
	echo "rweigel, t1p"
	twine upload -r $(REP) dist/hapiplotserver-$(VERSION).tar.gz --config-file misc/pypirc
	echo Uploaded to $(subst upload.,,$(URL))/project/hapiplotserver/

# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py

version-tag:
	git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags

# Use package in ./hapiplotserver instead of that installed by pip.
# This seems to not work in Spyder.
install-local:
	python setup.py install

install:
	pip install 'hapiplotserver==$(VERSION)' --index-url $(URL)simple
	conda list | grep hapiplotserver
	pip list | grep hapiplotserver

clean:
	- rm -rf $(TMPDIR)/hapi-data
	- python setup.py --uninstall
	- find . -name __pycache__ | xargs rm -rf {}
	- find . -name *.pyc | xargs rm -rf {}
	- find . -name *.DS_Store | xargs rm -rf {}
	- find . -type d -name __pycache__ | xargs rm -rf {}
	- find . -name *.pyc | xargs rm -rf {}
	- rm -f *~
	- rm -f \#*\#
	- rm -rf env dist build
	- rm -f MANIFEST
	- rm -rf .pytest_cache/
	- rm -rf *.egg-info/
