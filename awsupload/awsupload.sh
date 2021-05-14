#!/bin/sh
while true; do
    basepass=$(pwd)
    modelpass="${basepass}/models"
    aws s3 sync ${modelpass} s3://eeic2021-gameai-1
    #for foldername in $modelpass; do
    #    f=${foldername##*/}
    #    echo $f
    #    if grep -q $f ${basepass}/awsupload/uploadedfolders.txt; then
    #        echo uploaded;
    #    else
    #        echo upload;
    #        aws s3 cp ${foldername} s3://eeic2021-gameai-1/${f} --recursive
    #        echo $f >> ${basepass}/awsupload/uploadedfolders.txt
    #    fi    
    #done
    sleep 180;
done