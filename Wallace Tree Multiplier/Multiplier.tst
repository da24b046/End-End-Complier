load Multiplier.hdl,
output-file Multiplier.out,
compare-to Multiplier.cmp,
output-list a%B1.16.1 b%B1.16.1 outlow%B1.16.1 outhigh%B1.16.1;

set a %B0000000000000000,
set b %B0000000000000000,
eval, output;

set a %B0000000000000001,
set b %B0000000000000001,
eval, output;

set a %B0000000011111111,
set b %B0000000011111111,
eval, output;

set a %B0000000100000000,
set b %B0000000100000000,
eval, output;

set a %B1010101010101010,
set b %B0101010101010101,
eval, output;

set a %B1111111111111111,
set b %B1111111111111111,
eval, output;

set a %B0000000000000010,
set b %B0000000000000010,
eval, output;

set a %B0000000000000011,
set b %B0000000000000101,
eval, output;

set a %B0000000000001111,
set b %B0000000000001111,
eval, output;

set a %B0000000000010000,
set b %B0000000000010000,
eval, output;

set a %B0000000000011111,
set b %B0000000000011111,
eval, output;

set a %B0000000001111111,
set b %B0000000001111111,
eval, output;

set a %B0000001111111111,
set b %B0000000000000011,
eval, output;

set a %B0001000000000000,
set b %B0000000000001000,
eval, output;

set a %B0011000000111001,
set b %B0000000000000010,
eval, output;

set a %B1000000000000000,
set b %B0000000000000010,
eval, output;