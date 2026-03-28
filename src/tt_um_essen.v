/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
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

reg [W-1:0]   res_q;
reg [2*W-1:0] data_q;
reg [3:0]     data_v_q;


wire       data_v;  
wire [1:0] data_idx; 
wire       start_mul_next;

assign data_v   = uio_in[0];

always @(posedge clk) begin
	if(data_v) begin
		data_q <= {data_q[24:0], ui_in};
	end
end

assign start_mul_next = |data_v_q;

always @(posedge clk) begin
	if (~rst_n) begin
		start_mul_q <= 1'b0;
		data_v_q <= 4'b0;
	end else begin
		if (ena) begin
			start_mul_q <= start_mul_next;	
			data_v_q <= start_mul_next ? { 3'b0, data_v }:
						data_v ? {data_v_q[2:0], 1'b1}:
						data_v_q;
		end
	end
end


bf16_mul m_mul(
	.sa_i(data_q[15]),
	.ea_i(data_q[14:7]),
	.ma_i(data_q[6:0]),
	.sb_i(data_q[15]),
	.eb_i(data_q[14:7]),
	.mb_i(data_q[6:0]),
	.s_o(res_next[15]),
	.e_o(res_next[14:7]),
	.m_o(res_next[6:0])
);


reg [1:0] res_v_q; 

always @(posedge clk) begin
	if (~rst_n) res_v_q <= 2'b0;
	else res_v_q <= {start_mul_q, res_v_q[1]};
	end 
end

always @(posedge clk) begin
	if (start_mul_q) res_q <= res_next; 
	else res_q <= { 8'b0, res_q[15:8] };
end

assign uo_out = res_q[7:0]
assign uio_out[6] = |res_v_q; // data 
assign uio_out[7] = |res_v_q | start_mul_q;// early;
endmodule
