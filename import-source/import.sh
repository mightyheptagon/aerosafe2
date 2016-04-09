#!/bin/bash

TABLES=$(mdb-tables -1 $1)

MUSER="aero"
MPASS="your password"
MDB="$2"

MYSQL=$(which mysql)

for t in $TABLES
do
    $MYSQL -u $MUSER -p$MPASS $MDB -e "DROP TABLE IF EXISTS $t"
done

mdb-schema $1 mysql | $MYSQL -u $MUSER -p$MPASS $MDB

for t in $TABLES
do
    mdb-export -D '%Y-%m-%d %H:%M:%S' -I mysql $1 $t | $MYSQL -u $MUSER -p$MPASS $MDB
done
