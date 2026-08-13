OPENQASM 3;
include "stdgates.inc";

qubit[3] q;

h q[0];
h q[1];
h q[2];

cx q[0], q[1];
rz(0.6) q[1];
cx q[0], q[1];

cx q[1], q[2];
rz(0.6) q[2];
cx q[1], q[2];

cx q[0], q[2];
rz(0.6) q[2];
cx q[0], q[2];

rx(1.0) q[0];
rx(1.0) q[1];
rx(1.0) q[2];

cx q[0], q[1];
rz(0.3) q[1];
cx q[0], q[1];

cx q[1], q[2];
rz(0.3) q[2];
cx q[1], q[2];

cx q[0], q[2];
rz(0.3) q[2];
cx q[0], q[2];

rx(0.8) q[0];
rx(0.8) q[1];
rx(0.8) q[2];

h q[0];
h q[0];
