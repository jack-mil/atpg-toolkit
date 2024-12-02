#!/usr/bin/env bash
set -x
./atpg-toolkit generate circuits/s349f_2.net 185-sa-1
./atpg-toolkit faults circuits/s349f_2.net 01XX11XXXX1XXXX0XXXXXXXX
./atpg-toolkit generate circuits/s344f_2.net 95-sa-0
./atpg-toolkit faults circuits/s344f_2.net X1XXXXXXXXX1XXXXXXXXXXXX
./atpg-toolkit generate circuits/s349f_2.net 179-sa-1
./atpg-toolkit generate circuits/s344ff_2.txt 191-sa-0
