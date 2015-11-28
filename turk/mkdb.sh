#!/bin/sh

FN=turk.db

if [ -f $FN ]
then
	echo Database $FN already exists.  Will not overwrite
	exit 1
fi
sqlite3 $FN < turk.schema

