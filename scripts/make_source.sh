#!/bin/bash

THISDIR=$(readlink -f $(dirname $0))

cd $THISDIR/..

TARBALL=$(mktemp -d)/fakerpm-$(cat VERSION).tar.gz

tar cfz $TARBALL .

[ $? -ne 0 ] && echo ' error: failed to create tarball' && exit 1

echo $TARBALL
