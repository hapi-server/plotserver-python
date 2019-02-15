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

PYTHON=python3.6

URL=https://upload.pypi.org
REP=pypi

# VERSION below is updated in "make version-update" step.
VERSION=0.0.3
SHELL:= /bin/bash

test:
	make test-repository

test-repository:
	make test-commandline PYTHON=python3.6
	make test-commandline PYTHON=python2.7
	- rm -rf $(TMPDIR)/hapi-data
	make test-script PYTHON=python3.6
	- rm -rf $(TMPDIR)/hapi-data
	make test-script PYTHON=python2.7

test-commandline:
	$(PYTHON) setup.py develop
	bash hapiplotserver/test/test_hapiplotserver.sh 

test-script:
	$(PYTHON) setup.py develop
	$(PYTHON) hapiplotserver/test/test_hapiplotserver.py

test-old:
	read -p "Press enter to continue tests."
	cd hapiplotserver; \
		gunicorn -w 4 -b 127.0.0.1:5000 'server:gunicorn(loglevel="debug",use_cache=False)' &
	read -p "Press enter to continue tests."
	echo("Open and check http://127.0.0.1:5000/")

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

# Does not work. 
#	source env/bin/activate && \
#		$(PYTHON) env/lib/$(PYTHON)/site-packages/hapiplotserver/test/test_hapiplotserver.py

#		bash env/lib/$(PYTHON)/site-packages/hapiplotserver/test/test_hapiplotserver.sh 

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
	make release-upload

release-upload: 
	twine upload \
		-r $(REP) dist/hapiplotserver-$(VERSION).tar.gz \
		--config-file misc/pypirc \
		&& \
	echo Uploaded to $(subst upload.,,$(URL))/project/hapiplotserver/


# Update version based on content of CHANGES.txt
version-update:
	python misc/version.py
	mv setup.py.tmp setup.py
	mv hapiplotserver/hapiplotserver.tmp hapiplotserver/hapiplotserver
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



















