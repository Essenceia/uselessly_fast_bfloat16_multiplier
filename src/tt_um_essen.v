/*
 * Copyright (c) 2026 Julia Desmazes
 * SPDX-License-Identifier: Apache-2.0
 */

`timescale 1ns / 1ps
`default_nettype none

module tt_um_essen (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
localparam W = 16;

wire [6:0]    io_unused; 

reg [2*W-1:0] data_q;
reg [3:0]     data_v_q;
wire          data_v;  

wire          start_mul;
reg           mul_delay_q;
wire          mul_res_v; 

reg [1:0]    res_v_q; 
reg [W-1:0]  res_q;
wire [W-1:0] res_next;

assign uio_oe = {2'b11, 6'h00};
assign uio_out[5:0] = 6'b0;

assign io_unused = uio_in[7:1];
assign data_v    = uio_in[0];

always @(posedge clk)
	if(data_v) data_q <= {data_q[23:0], ui_in};

assign start_mul = &data_v_q;
always @(posedge clk) begin
	if (~rst_n) begin
		data_v_q <= 4'b0;
	end else begin
		if (ena) begin
			data_v_q <= start_mul ? { 3'b0, data_v }:
						data_v ? {data_v_q[2:0], 1'b1}:
						data_v_q;
		end
	end
end

bf16_mul_fast m_mul(
	.clk(clk),
	.sa_i(data_q[31]),
	.ea_i(data_q[30:23]),
	.ma_i(data_q[22:16]),
	.sb_i(data_q[15]),
	.eb_i(data_q[14:7]),
	.mb_i(data_q[6:0]),
	.s_o(res_next[15]),
	.e_o(res_next[14:7]),
	.m_o(res_next[6:0])
);

always @(posedge clk)
	if (~rst_n) mul_delay_q <= 1'b0; 
	else mul_delay_q <= start_mul;

assign mul_res_v = mul_delay_q;

always @(posedge clk) begin
	if (~rst_n) res_v_q <= 2'b0;
	else res_v_q <= {mul_res_v, res_v_q[1]};
end

always @(posedge clk) begin
	if (mul_res_v) res_q <= res_next; 
	else res_q <= { 8'b0, res_q[15:8] };
end

assign uo_out = res_q[7:0];
assign uio_out[6] = |res_v_q; // data 
assign uio_out[7] = |res_v_q | mul_res_v;// early;
endmodule
