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
#    (Will fail unti new version is available at pypi.org for pip install. 
#     Sometimes takes ~5 minutes even though web page is immediately
#     updated.)
# 4. After package is finalized, create new version number in CHANGES.txt ending
#    with "b0" in setup.py and then run make version-update.

PYTHON=python3.6

URL=https://upload.pypi.org
REP=pypi

# VERSION below is updated in "make version-update" step.
VERSION=0.0.5-beta
SHELL:= /bin/bash

test:
    make test-virtualenv PYTHON=python3.6
    make test-virtualenv PYTHON=python2.7
	make test-repository PYTHON=python3.6
    make test-repository PYTHON=python2.7

test-repository:
	- rm -rf $(TMPDIR)/hapi-data
	pip uninstall -y -q hapiplotserver
	$(PYTHON) setup.py develop
	bash hapiplotserver/test/test_hapiplotserver.sh  # TODO: Need to pass $(PYTHON) to script.
	- rm -rf $(TMPDIR)/hapi-data
	pip uninstall -y -q hapiplotserver
	$(PYTHON) setup.py develop
	$(PYTHON) hapiplotserver/test/test_hapiplotserver.py

test-virtualenv:
	rm -rf env
	$(PYTHON) -m virtualenv env
	source env/bin/activate && \
	    pip install pytest && \
        pip install . && \
        pip install ../client-python
	source env/bin/activate && \
	    bash hapiplotserver/test/test_hapiplotserver.sh
	source env/bin/activate && \
	    python hapiplotserver/test/test_hapiplotserver.py

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
	make version-tag
	make package
	make release-upload

release-upload:
	echo "rweigel, t1p"
	twine upload -r $(REP) dist/hapiplotserver-$(VERSION).tar.gz --config-file misc/pypirc
	echo Uploaded to $(subst upload.,,$(URL))/project/hapiplotserver/

# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py
	mv setup.py.tmp setup.py
	mv hapiplotserver/hapiplotserver.tmp hapiplotserver/hapiplotserver
	mv hapiplotserver/main.py.tmp hapiplotserver/main.py
	mv Makefile.tmp Makefile

version-tag:
	git commit -a -m "Last $(VERSION) commit"
	git push
	git tag -a v$(VERSION) -m "Version "$(VERSION)
	git push --tags

# Use package in ./hapiplotserver instead of that installed by pip.
# This seems to not work in Spyder.
install-local:
	python setup.py

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





























