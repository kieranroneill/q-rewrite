OPENQASM 3;
include "stdgates.inc";

qubit[2] q;

h q[0];
cx q[0], q[1];

x q[0];
x q[0];

cx q[0], q[1];
