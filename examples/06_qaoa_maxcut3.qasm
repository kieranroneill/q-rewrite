OPENQASM 3;
include "stdgates.inc";

qubit[3] q;

h q[0];
h q[1];
h q[2];

cx q[0], q[1];
rz(0.7) q[1];
cx q[0], q[1];

cx q[1], q[2];
rz(0.7) q[2];
cx q[1], q[2];

cx q[0], q[2];
rz(0.7) q[2];
cx q[0], q[2];

rx(1.1) q[0];
rx(1.1) q[1];
rx(1.1) q[2];

rz(0.4) q[0];
rz(-0.4) q[0];
