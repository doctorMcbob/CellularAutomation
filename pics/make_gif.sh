#!/bin/bash
s=""
for ((n=0;n<=31;n++))
do
	s="${s} ${n}.png"
done

convert -delay 60 -loop 0  ${s} automata.gif

