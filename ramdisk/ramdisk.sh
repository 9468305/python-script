#!/bin/bash
RAMDISK="ramdisk"
SIZE=6144   #size in MB for ramdisk.
diskutil erasevolume HFS+ $RAMDISK `hdiutil attach -nomount ram://$[SIZE*2048]`
