#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CPI_DIR="/Volumes/CIRCUITPY"

GIT_DIR_CODE="$SCRIPT_DIR/code"
GIT_DIR_SCRIPTS="$GIT_DIR_CODE/scripts"
GIT_DIR_LIB="$GIT_DIR_CODE/lib"

CPI_DIR_CODE="$CPI_DIR"
CPI_DIR_SCRIPTS="$CPI_DIR/scripts"
CPI_DIR_LIB="$CPI_DIR/lib"


arg=$1

if [[ "$arg" == "to_pico" ]];then
	echo "foo"

elif [[ "$arg" == "to_git" ]];then
	cp $CPI_DIR_CODE/s*py $GIT_DIR_CODE
	cp $CPI_DIR_SCRIPTS/*scode $GIT_DIR_SCRIPTS
	cp $CPI_DIR_LIB/s*py $GIT_DIR_LIB
else
	echo "no arg provided"
	exit 1
fi



