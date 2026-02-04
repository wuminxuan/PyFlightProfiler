#!/bin/sh
pid=$1

IS_DARWIN=false
if [ "$(uname -s)" = "Darwin" ]; then
    IS_DARWIN=true
fi

if [ "$IS_DARWIN" = "false" ]; then
    bin_path=`readlink  /proc/${pid}/exe`
else
    bin_path=$(lsof -a -p ${pid} -d txt -Fn | cut -c2- |grep -E "Python$|python[0-9.]*$" |head -n 1)
fi
echo $bin_path
