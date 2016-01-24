#!/bin/bash

cur=`pwd`
pushd ../compiler/min-caml/test && cat ../libmincaml.ml huga.ml > hugahuga.ml && cd .. && make byte-code && ./min-caml test/hugahuga > ./output && mv test/hugahuga.s ${cur}/hugahuga.s && popd && ./native.sh hugahuga.s
