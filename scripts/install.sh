DESTDIR=${DESTDIR:-/}

[ ! -d $DESTDIR ] && echo " error: invalid directory '$DESTDIR'" && exit 1

SHAREDIR=$DESTDIR/usr/share/fakerpm
BINDIR=$DESTDIR/usr/bin

# directories
install -m 0755 -d $SHAREDIR
install -m 0755 -d $BINDIR

# files
install -m 0755 fakerpm $BINDIR
install -m 0644 README.rst $SHAREDIR
install -m 0644 LICENSE $SHAREDIR
install -m 0644 VERSION $SHAREDIR
