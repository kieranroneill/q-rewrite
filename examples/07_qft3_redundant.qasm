OPENQASM 3;
include "stdgates.inc";

qubit[3] q;

h q[0];
cp(pi / 2) q[1], q[0];
cp(pi / 4) q[2], q[0];

h q[1];
cp(pi / 2) q[2], q[1];

h q[2];

swap q[0], q[2];

rz(0.3) q[1];
rz(-0.3) q[1];
