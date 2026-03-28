# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, with_timeout
from cocotb.types import LogicArray

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

async def test_mul(dut):
	dut.uio_in.value = 0 
	dut.ui_in.value = LogicArray("XXXXXXXX",8)
	await ClockCycles(dut.clk, 2)
	dut.uio_in.value = 1
	dut.ui_in.value = 0
	await ClockCycles(dut.clk, 4)
	dut.uio_in.value = 0
	dut.ui_in.value = LogicArray("XXXXXXXX",8)
	await ClockCycles(dut.clk, 10)
 
@cocotb.test()
async def test_project(dut):
	dut._log.info("Trust me bro")
	await rst(dut)
	await test_mul(dut)

