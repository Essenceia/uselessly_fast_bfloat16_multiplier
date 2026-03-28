# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, with_timeout
from cocotb.types import LogicArray
import random 

def start_clk(dut):
	clock = Clock(dut.clk, 2, "us")
	cocotb.start_soon(clock.start()) #runs the clock "in the background" 


async def rst(dut, ena=1):
	dut.rst_n.value = 0
	dut.uio_in.value = 0
	clk_task = start_clk(dut)
	await ClockCycles(dut.clk, 10) 
	dut.rst_n.value = 1
	dut.ena.value = 1
	await ClockCycles(dut.clk, 10)

async def invalid_data(dut, cycles):
	for i in range(0, cycles):
		dut.uio_in.value = 0
		dut.ui_in.value = LogicArray("XXXXXXXX",8)
		await ClockCycles(dut.clk,1)

# sending input values : A * B
async def send_input(dut, A, B):
	data = LogicArray(str(A)+ str(B))
	for i in range(0,4):
		if (random.randrange(0,100) > 75):
			await invalid_data(dut, random.randrange(1,5))
		dut.ui_in.value = data[(3-i)*8+7:(3-i)*8] 
		dut.uio_in.value = 1
		await ClockCycles(dut.clk, 1)
	dut.uio_in.value = 0
	dut.ui_in.value = LogicArray("XXXXXXXX",8)


async def read_res(dut):
	res = LogicArray(0x00000, 16)
	# wait for prop 
	assert(dut.uio_out.value[7] == 0)
	assert(dut.uio_out.value[6] == 0)
	await ClockCycles(dut.clk, 2)
	
	# check early 
	assert(dut.uio_out.value[7] == 1)
	assert(dut.uio_out.value[6] == 0)
	await ClockCycles(dut.clk, 1)
	
	# check res
	for i in range(0,2):
		assert(dut.uio_out.value[7] == 1)
		assert(dut.uio_out.value[6] == 1)
		res[i*8+7:i*8] = dut.uo_out.value
		await ClockCycles(dut.clk, 1)
	return res	

# A * B = C
async def test_case(dut, A, B, C):
	await send_input(dut, A, B)
	# read output
	res = await read_res(dut)
	if (res != C): 
		cocotb.log.error("Expected match failed for 16'h%s*16'h%s", hex(A), hex(B)) 
		cocotb.log.error("res 16'h%s 16'b%s", hex(res), res)
		cocotb.log.error("C   16'h%s 16'b%s", hex(C), C)
	assert(res == C)	

async def test_xprop(dut):
	dut.uio_in.value = 0 
	dut.ui_in.value = LogicArray("XXXXXXXX",8)
	await ClockCycles(dut.clk, 2)
	# send data
	await send_input(dut, LogicArray(0x0000,16), LogicArray(0x0000,16))

	res = await read_res(dut)
	assert(res == 0)	

@cocotb.test()
async def test_basic(dut):
	await rst(dut)
	await test_xprop(dut)
	await ClockCycles(dut.clk, 10)

@cocotb.test()
async def test_directed(dut):
	await rst(dut)
	await test_case(dut, LogicArray(0x4000, 16), LogicArray(0x4000,16), LogicArray(0x4080,16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0x3f80,16), LogicArray(0x3f80,16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0x3f80, 16), LogicArray(0x3f80, 16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0x4000, 16), LogicArray(0x4000, 16))
	await test_case(dut, LogicArray(0xbf80, 16), LogicArray(0x3f80, 16), LogicArray(0xbf80, 16))
	await test_case(dut, LogicArray(0xbf80, 16), LogicArray(0xbf80, 16), LogicArray(0x3f80, 16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0xc000, 16), LogicArray(0xc000, 16))
	await test_case(dut, LogicArray(0x3fc0, 16), LogicArray(0x3fc0, 16), LogicArray(0x4010, 16))
	await test_case(dut, LogicArray(0x4040, 16), LogicArray(0x4040, 16), LogicArray(0x4110, 16))
	await test_case(dut, LogicArray(0x4120, 16), LogicArray(0x4120, 16), LogicArray(0x42c8, 16))
	await test_case(dut, LogicArray(0x3580, 16), LogicArray(0x3f80, 16), LogicArray(0x3580, 16))
	await test_case(dut, LogicArray(0x4000, 16), LogicArray(0x3580, 16), LogicArray(0x3600, 16))
	await test_case(dut, LogicArray(0x4780, 16), LogicArray(0x3f80, 16), LogicArray(0x4780, 16))
	await test_case(dut, LogicArray(0x4000, 16), LogicArray(0x4780, 16), LogicArray(0x4800, 16))
	await test_case(dut, LogicArray(0x3e80, 16), LogicArray(0x3f80, 16), LogicArray(0x3e80, 16))
	await test_case(dut, LogicArray(0x4100, 16), LogicArray(0x3f80, 16), LogicArray(0x4100, 16))
	await test_case(dut, LogicArray(0x3880, 16), LogicArray(0x3f80, 16), LogicArray(0x3880, 16))
	await test_case(dut, LogicArray(0x4300, 16), LogicArray(0x3f80, 16), LogicArray(0x4300, 16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0x3e00, 16), LogicArray(0x3e00, 16))
	await test_case(dut, LogicArray(0xbf80, 16), LogicArray(0x4000, 16), LogicArray(0xc000, 16))
	await test_case(dut, LogicArray(0xc000, 16), LogicArray(0x3f80, 16), LogicArray(0xc000, 16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0x40a0, 16), LogicArray(0x40a0, 16))
	await test_case(dut, LogicArray(0x4040, 16), LogicArray(0x3f80, 16), LogicArray(0x4040, 16))
	await test_case(dut, LogicArray(0x3f40, 16), LogicArray(0x3f40, 16), LogicArray(0x3f10, 16))
	await test_case(dut, LogicArray(0x4500, 16), LogicArray(0x3f80, 16), LogicArray(0x4500, 16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0x4500, 16), LogicArray(0x4500, 16))
	await test_case(dut, LogicArray(0x3b80, 16), LogicArray(0x3f80, 16), LogicArray(0x3b80, 16))
	await test_case(dut, LogicArray(0x4000, 16), LogicArray(0x3b80, 16), LogicArray(0x3c00, 16))
	await test_case(dut, LogicArray(0x4a00, 16), LogicArray(0x3f80, 16), LogicArray(0x4a00, 16))
	await test_case(dut, LogicArray(0xbf80, 16), LogicArray(0x4040, 16), LogicArray(0xc040, 16))
	await test_case(dut, LogicArray(0x3f80, 16), LogicArray(0x3f40, 16), LogicArray(0x3f40, 16))
	await test_case(dut, LogicArray(0x4280, 16), LogicArray(0x4280, 16), LogicArray(0x4580, 16))
