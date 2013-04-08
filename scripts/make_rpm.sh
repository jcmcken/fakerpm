#!/bin/bash

! which rpm && echo ' error: the "rpm" utility could not be found' && exit 1

! which rpmbuild && echo ' error: the "rpmbuild" utility could not be found' && exit 1

SOURCEDIR=$(rpm --eval %{_sourcedir})
TARBALL=$(./scripts/make_source.sh)
TMPDIR=$(dirname $TARBALL)

mv $TARBALL $SOURCEDIR
rm -rf $TMPDIR

rpmbuild -ba ext/fakerpm.spec
