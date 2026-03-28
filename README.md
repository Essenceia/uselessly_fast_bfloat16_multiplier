# Uselessly fast bfloat16 multplier ASIC

This repo contains an very high frequency bfloat16 multiplier ASIC macro taped out as part of the Tiny Tapeout `iph0p4` experimental shuttle, 
targetting IHP's experiemental 130 nm CMOS `sg13cmos5l` node. 

This bfloat16 multiplier was designed as of a maximum frequency chanenge can operate at upto 463.92 MHz on norminal operating corner of 1p20V at 25C and . 

# Max frequency challenge 

This design was build as friendly competition agains [NikLeberg](https://github.com/NikLeberg/tt_um_float_synth/tree/ihp-sg13cmos5l), 
to see which of us could take the crown for the highest possible maximum frequency floating point multiplier on the nominal corner. 

Each of us is using a different floating point type for our multiplier : 
- tt_um_float_synth, Nik, uses a a designing for a float8 with denomals and $\infy$ support, without `NaN`s, and using round to zero rounding. 
- tt_um_essen, this design, is designing for a bfloat16 without denormals, $\infty$ or `NaN`s, and also using rount to zero rounding.

## Timing optimization strategy 

Intrestingly, each of us chose a very different stategy for optimizing our timing. 

### Synthesizer driven 

Nik chose a tooling focused strategy with a strong emphisis on synthesis optimization, and more specifically backwards looking retiming. 
The main idea of the retiming driven frequency optimizatoin was to introduce extra empty cycle after the logic and let the synthesizer automatically spread the logic accross these availble 
cycles. [The full explaination can be found in the tt_um_float's documentation](https://github.com/NikLeberg/tt_um_float_synth/blob/ihp-sg13cmos5l/docs/info.md).

By pipelining the floatpoint multiplication over 8 cycles this design managed to reach a maximum operating frequency of `550 MHz`, taking the crown for this chalenge.  

### RTL driven 


I chose in this `tt_um_essen` project to optimized timing though the more manual approach of RTL refinement: but investing extra effort in reducing logic depth on the cirtical path, and by trading off 
wider logic for shallower paths. 


## IO bottleneck

Both of us are well aware the the chip's IO is unlikely to reach a stable operating regime above 75MHz on the 
output path and 100MHz on the input path.

Because of this, if this experimental chip is functional, these designs will needed to be clocked 
in accordance with the output IO limitation. 

## E
