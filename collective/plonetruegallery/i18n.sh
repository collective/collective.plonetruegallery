#!/bin/sh

# This script must be executed from the folder it's located in
# i18ndude should be available in current $PATH

I18N_DOMAIN="collective.plonetruegallery"


i18ndude rebuild-pot --pot locales/${I18N_DOMAIN}.pot --create ${I18N_DOMAIN} --merge locales/manual.pot ./


for file in `find locales -name *.po`
do
    echo Syncing $file ...
    i18ndude sync --pot locales/${I18N_DOMAIN}.pot $file
    msgfmt -o `dirname $file`/`basename $file .po`.mo $file --no-hash
done
