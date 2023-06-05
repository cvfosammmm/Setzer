#!/bin/sh

cd "$(dirname "$(realpath "$0")")/.."

echo "# generated on $(date -u)" > ./po/POTFILES

echo "" >> ./po/POTFILES
echo "./data/org.cvfosammmm.Setzer.metainfo.xml.in" >> ./po/POTFILES

echo "" >> ./po/POTFILES
find ./setzer -name '*.py' | sort >> ./po/POTFILES
