#!/bin/bash

rm -rf ./ast/$2.json
#touch ./ast/$2.json
~/node_modules/solidity-parser/cli.js $1 > ./ast/$2.json
