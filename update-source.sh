#!/bin/sh
# product name
product=chrome
# name
name=google-$product
# this package
specfile=$name.spec
# arch to check package. irrelevant for actual arch
arch=x86_64
# branch: stable, beta, unstable. default: stable
branch=${1:-stable}

case "${branch}" in
	stable|beta|unstable)
		;;
	*)
		echo "$0: Unknown branch: $branch. Supported branches: stable, beta, unstable." >&2
		exit 1
		;;
esac

sourceurl=http://dl.google.com/linux/$product/rpm/stable/$arch

set -e

echo -n "Fetching latest version... "
t=$(mktemp)

# poldek is buggy, see https://bugs.launchpad.net/poldek/+bug/1026762
#poldek -q --st=metadata --source "$sourceurl/" --update
#poldek -q --skip-installed --st=metadata --source "$sourceurl/" --cmd "ls google-chrome-$branch" > $t

repodata=primary-$branch-$(date +%Y%m%d).xml
test -e $repodata || {
	wget -c $sourceurl/repodata/primary.xml.gz
	gzip -dc primary.xml.gz > $repodata || test -s $repodata
}
perl -ne 'm{<name>google-'$product-$branch'</name>} and m{<version epoch="0" ver="([\d.]+)" rel="(\d+)"/>} and print "$1 $2"' > $t < $repodata

set -- $(sed -re "s,^.+-([^-]+)-([^-]+).$arch$,\1 \2," $t)

ver=$1
rev=$2

# extract flash version
rpm=$name-$branch-$ver-$rev.$arch.rpm
manifest=manifest-$ver.json
test -e $rpm || wget -c $sourceurl/$rpm
test -e $manifest || {
	echo ./opt/google/chrome/PepperFlash/manifest.json > $t
	rpm2cpio $rpm | cpio -i -E $t --to-stdout > manifest-$ver.json
}
flashv=$(awk -F'"' '/version/{print $4}' manifest-$ver.json)

rm -f $t
echo "$ver-$rev"

oldrev=$(awk '/^%define[ 	]+svnrev[ 	]+/{print $NF}' $specfile)
oldflash=$(awk '/^%define[ 	]+flashv[ 	]+/{print $NF}' $specfile)
if [ "$oldrev" = "$rev" -a "$oldflash" = "$flashv" ]; then
	echo "Already up to date"
	exit 0
fi

echo "Updating $specfile for $ver r$rev"
sed -i -e "
	s/^\(%define[ \t]\+svnrev[ \t]\+\)[0-9]\+\$/\1$rev/
	s/^\(%define[ \t]\+state[ \t]\+\)[a-z]\+\$/\1$branch/
	s/^\(%define[ \t]\+flashv[ \t]\+\)[0-9.]\+\$/\1$flashv/
	s/^\(Version:[ \t]\+\)[.0-9]\+\$/\1$ver/
" $specfile
../builder -ncs -g $specfile || :
../builder -ncs -5 $specfile
