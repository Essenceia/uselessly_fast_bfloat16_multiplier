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
		dut.ui_in.value = data[i*8+7:i*8] 
		dut.uio_in.value = 1
		await ClockCycles(dut.clk, 1)


async def test_xprop(dut):
	dut.uio_in.value = 0 
	dut.ui_in.value = LogicArray("XXXXXXXX",8)
	await ClockCycles(dut.clk, 2)
	# send data
	await send_input(dut, LogicArray(0x0000,16), LogicArray(0x0000,16))
	
	# wait for prop 
	dut.ui_in.value = LogicArray("XXXXXXXX",8)
	dut.uio_in.value = 0
	assert(dut.uio_out.value[7] == 0)
	assert(dut.uio_out.value[6] == 0)
	await ClockCycles(dut.clk, 2)
	
	# check early 
	assert(dut.uio_out.value[7] == 1)
	assert(dut.uio_out.value[6] == 0)
	await ClockCycles(dut.clk, 1)
	
	# check res
	for i in range(0,1):
		assert(dut.uio_out.value[7] == 1)
		assert(dut.uio_out.value[6] == 1)
		assert(dut.uo_out.value == 0)
		await ClockCycles(dut.clk, 1)
 
@cocotb.test()
async def test_project(dut):
	await rst(dut)
	await test_xprop(dut)
	await ClockCycles(dut.clk, 10)

