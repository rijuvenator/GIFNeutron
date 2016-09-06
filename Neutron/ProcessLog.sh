#!/bin/bash

# Takes in a eventG4log (argument 1) and cleans it
# Outputs a file ready for reading by makeTree

if [ -z "$1" ]
then
	echo "Usage: ProcessLog.sh EVENTG4LOG"
	exit
fi

  echo -e "Now processing: ${1}..."
# Get rid of messages: delete all lines between %MSG, inclusive
sed -i '/^\%MSG/,/^\%MSG/d' $1
  echo "MSG removed..."
# Delete from beginning till "Event #1"
sed -i '1,/Event #1/d' $1
  echo "Top matter removed..."
# Delete the first line, which is empty
sed -i '1d' $1
  echo "First line removed..."
# Delete from an empty line (which SHOULD be only at the end) till the end of the file
sed -i '/^$/,$d' $1
  echo "End matter removed..."
# Add a line of 105 stars
for i in {1..105}; do printf '*'; if [ $i == '105' ]; then echo ''; fi; done >> $1
  echo "Stars added..."
  echo "Done."
