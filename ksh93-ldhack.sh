#!/bin/sh

sonam=`echo "$@" | sed 's/.*-o \(lib[A-Za-z]\+\.so\.[0-9\.]\+\).*/\1/'`

if [ -n "$sonam" ] ; then
	/usr/bin/ld -soname $sonam $@
else
	/usr/bin/ld $@
fi
