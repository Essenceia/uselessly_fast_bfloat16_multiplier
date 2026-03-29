# Uselessly fast bfloat16 multplier ASIC

This repo contains an very high frequency bfloat16 multiplier ASIC macro taped out as part of the Tiny Tapeout `iph0p4` experimental shuttle, 
targetting IHP's experiemental 130 nm CMOS `sg13cmos5l` node. 

This bfloat16 multiplier was designed as of a maximum frequency chanenge can operate at upto 454.545 MHz on norminal operating corner of 1p20V at 25C and . 

# Max frequency challenge 

This design was build as friendly competition agains [NikLeberg](https://github.com/NikLeberg/tt_um_float_synth/tree/ihp-sg13cmos5l), 
to see which of us could take the crown for the highest possible maximum frequency floating point multiplier on the nominal corner. 

Each of us is using a different floating point type for our multiplier : 
| Designer       | Module                | Floating Point Type | Denormals | Infinity | NaN | Rounding Mode   |
|----------------|-----------------------|---------------------|-----------|----------|-----|-----------------|
| NikLebery      | `tt_um_float_synth`   | float8             | Yes       | Yes      | No  | RTZ (Round to zero)   |
| Essenceia   | `tt_um_essen`         | bfloat16           | No        | No       | No  | RTZ (Round to zero)  |

## Timing optimization strategy 

Intrestingly, each of us chose a very different stategy for optimizing our timing. 

### Synthesizer driven 

Nik chose a tooling focused strategy with a strong emphisis on synthesis optimization, and more specifically backwards looking retiming. 
The main idea of the retiming driven frequency optimizatoin was to introduce extra empty cycle after the logic and let the synthesizer automatically spread the logic accross these availble 
cycles. [The full explaination can be found in the tt_um_float's documentation](https://github.com/NikLeberg/tt_um_float_synth/blob/ihp-sg13cmos5l/docs/info.md).


![synth result](docs/pipe.webp)
Synthesis json results rendered using `LintyServices.linty-graphviz` by NikKeberg, all credit belongs to him.

By pipelining the floatpoint multiplication over 8 cycles this design managed to reach a maximum operating frequency of `550 MHz`, taking the crown for this chalenge.  

### RTL driven 

I chose in this `tt_um_essen` project to optimized timing though the more manual approach of RTL refinement: but investing extra effort in reducing logic depth on the cirtical path, and by trading off 
wider logic for shallower paths. This was made much simpler since I had implemented the `bfloat16` multiplication logic from scratch and as such has pre-exiting intutions about which 
paths would be my critical paths once implemented. 

Unlike the `tt_um_float_synth`, `tt_um_essen` only has a 8 bit long interface, and so needs 4 cycles to shift in all the data for a multiplication. It also need 2 cycles to stream out the result given the output
data bus width is also 8 bits. Although I will not be counting these cycles as being part of the floating point multiplication, for full transparancy I would like to state that the fact that they are less deep stages does help the multiplication's timing a bit. 

The bfloat16 multiplication was cut into 2 cycles for improving performance. 
As expected, the most major critical path when though the mantissa multiplication. unfortunatly, in the original implementation of the multiplication module we 
where using the synthesizer to infer an unsigned booth radix4 multiplier. Thus, in order to help pipeline this path, I needed to re-implement an 8 bit unsigned booth radix4 multiplier. The multiplication staged as then pipelined after the encoding stage and in the middle of the compression stage. We are storing the partial compression of the first two partial products, and the last 3 before compressing them together to get the final result on the next cycle. 

A few additional such implementation where performed though the multiplier allowing this design to reach a maximum operating frequency of `454.545` MHz.

## Competition results 

This competition was won hands down by nearly a full 100MHz margin by NikLeber 👑 

| Designer       | Module                | Floating Point Type | Fmul cycles | Fmax | 
|----------------|-----------------------|---------------------|-----------|----------|
| NikLebery      | `tt_um_float_synth`   | float8             | 8      | 550 MHz      |
| Essenceia   | `tt_um_essen`         | bfloat16           | 2        | 454 MHz       | 

## IO bottleneck

Both of us are well aware the the chip's IO is unlikely to reach a stable operating regime above 75MHz on the 
output path and 100MHz on the input path.

Because of this, if this experimental chip is functional, these designs will needed to be clocked 
in accordance with the output IO limitation. 
