#!/usr/bin/env bash

appdir=`dirname $0`
start_url=$1

count=10
if [ "" != "$2" ]; then
    count=$2
fi

TXT_STORE=`cat $appdir/sinablog_scrapy/settings.py | grep TXT_STORE | grep -v grep | awk -F= '{print $2}' | awk -F"'" '{print $2}'`

for adir in `cat $appdir/sinablog_scrapy/settings.py | grep STORE | grep -v grep | awk -F= '{print $2}' | awk -F"'" '{print $2}'`
do
    mkdir -p $adir
done

while [ true ]; do

    if [ "" !=  "$start_url" ]; then
        echo "================================================================================"
        echo "start url found $start_url"
        echo "================================================================================"
        url=$start_url
        start_url=""
        ls ${TXT_STORE}/* | xargs rm -f

    else
        afile=`ls -t ${TXT_STORE}/* | grep 'prev' | grep -v 'grep' | head -1`
        if [ -f "$afile" ]; then
            url=`cat $afile | tail -1`
        fi
        rm -f $afile

        if [ "" = "$url" ]; then
            echo "================================================================================"
            echo "Finished crawling"
            echo "================================================================================"
            exit 0
        else
            echo "================================================================================"
            echo "next url found: $url"
            echo "================================================================================"
        fi

    fi

    echo "[`date`] start to crawl '$url' .... " 
    python $appdir/sina.py  $url

    python $appdir/text2docx.py
    echo "[`date`] finished to crawl '$url' "
    url=""
    ls ${TXT_STORE}/* | grep -v prev | xargs rm -f

    count=$((count - 1))
    if [ $count -le 0 ]; then
        exit 0
    fi

    sleep $((RANDOM % 11 + 2 ))

done
