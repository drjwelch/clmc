Demo programs intended for GCSE
===============================

variable.lmc
------------
Input a value (your age)
Store in the location labelled 'age'
Load from 'age' and output
"A variable is a named location in memory where data is stored"

addone.lmc
----------
Add one to the input value and output it
Change 'one' to 'sausages' in both places - does it make a difference?
So does the name of a variable (its identifier) tell you about its value?

if-else.lmc
-----------
Demonstrates selection (IF/ELSE)
Decision / IF statements are branches in LMC
BRP specifically is "IF ACC>=0 ..."

bigof2.lmc
----------
Find largest of two numbers
Can you modify to output the larger number rather than 1 or 2?

do-loop.lmc
-----------
Repeat until input is zero
Can you modify to a different condition e.g. input>5?
Modify to while/for is much more challenging

countdown.lmc
-------------
Simple loop; countdown from input number
Why does it end at -1 not 0?
Loops are ALSO branches in LMC


Demo programs intended for A level use
======================================

Many use addressing modes other than the standard LMC set
These modes are part of the A level syllabus but not GCSE
Able GCSE students might like mult and divide (non-extended)

trinum.lmc
----------
A program to check if an input number is a triangle number.
From http://www.yorku.ca/sychen/research/LMC/LMCExample.html.

sum-array.lmcx
--------------
Calculates and outputs the sum of a 1D array (list) of numbers
Uses indexed addressing (requires extended mode)

mult.lmc, divide.lmc
--------------------
Multiply/divide by repeated addition/subtraction

mult.lmcx, divide.lmcx
----------------------
Multiply/divide using shift and add/sub
Uses shift instructions (requires extended mode)

lifo-stack-methods.lmcx
-----------------------
Stack simulation; enter values to push; enter -1 to pop
Pop from empty stack to exit
Uses indirect addressing (requires extended mode)

fifo-queue-methods.lmcx
-----------------------
As for lifo but with queue

indexed-simple example.lmcx
---------------------------
Simple demo of use of indexed addressing
Adds constant (5) to all values in an array
Uses indexed addressing (requires extended mode)

indirect-simple example.lmcx
----------------------------
Simple demo of use of indirect addressing
Adds a pointer to store two values in different locations
Uses indirect addressing (requires extended mode)

bubble-selfmodifying.lmc
------------------------
Bubble sort - uses self-modifying code
Only for the most very able at A level!

bubble.lmcx
-----------
Bubble sort an array
Uses indexed addressing (requires extended mode)

