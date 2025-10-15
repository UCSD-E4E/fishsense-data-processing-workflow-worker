#! /bin/bash

mkdir -p ./data
if ! findmnt ./data; then
    sudo mount -v -t cifs -o vers=3,credentials=$E4E_NAS_CREDS,uid=`whoami`,ro "//e4e-nas.ucsd.edu/fishsense_data" ./data
fi

mkdir -p ./intrinsics
if ! findmnt ./intrinsics; then
    sudo mount -v -t cifs -o vers=3,credentials=$E4E_NAS_CREDS,uid=`whoami`,ro "//e4e-nas.ucsd.edu/fishsense/Fishsense Lite Calibration Parameters" ./intrinsics
fi

mkdir -p ./output
if ! findmnt ./output; then
    sudo mount -v -t cifs -o vers=3,credentials=$E4E_NAS_CREDS,uid=`whoami` "//e4e-nas.ucsd.edu/fishsense_process_work" ./output
fi