#!/bin/bash

DIR=$(dirname "$0")/..

# Kill old processes
echo "test_hapiplotserver.sh: Killing any running hapiplotserver listening on port 5001."
pkill -f "hapiplotserver --port 5001"

which hapiplotserver

# Start server
cmd="hapiplotserver --port 5001 --workers 2 --loglevel debug &"
echo "test_hapiplotserver.sh: Starting server using $cmd"
eval $cmd

PID=$!

echo "test_hapiplotserver.sh: Sleeping for 2 seconds before running tests."
sleep 3

echo "test_hapiplotserver.sh: Running tests."

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Very basic test: If filesize is larger than 60k, 
# it is assumed to have plotted; the error image for
# the server is 36k.
# TODO: Modify headers for server to have "X-Error" 
# if error (an so error image is returned).
# TODO: Do this loop in a Python script so headers can be inspected.
# In script do test with many requests in parallel.
urls=`cat $DIR/test/urls.txt`
for url in $urls;
do
	#Split string of form expect;url in line of file
	#url=${url#*;}
	#expect=${url%%;*}
	echo "test_hapiplotserver.sh: Testing: $url"
	curl -s $url > $TMPDIR/a.png
	curl -s $url > ~/Desktop/a.png
	#ls -lh $TMPDIR/a.png
	if [[ "$(find $TMPDIR/a.png -maxdepth 1 -size +60k)" == "$TMPDIR/a.png" ]]; then
		echo -e "test_hapiplotserver.sh: ${GREEN}PASS${NC}."
	else
		echo -e "test_hapiplotserver.sh: ${RED}FAIL${NC}."
	fi
	rm -f $TMPDIR/a.png
done

echo "test_hapiplotserver.sh: Stopping server."
kill -s "SIGINT" $PID
