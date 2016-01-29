#!/bin/bash

cur=`pwd`
pushd ../compiler/min-caml/test && cat ../libmincaml.ml globals.ml min-rt.ml > hoge.ml && cd .. && make byte-code && ./min-caml test/hoge > ./output && mv test/hoge.s ${cur}/hoge.s && popd && ./native.sh hoge.s && diff ./stdout ./stdout.mincaml
