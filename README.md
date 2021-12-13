# tunnel-tests

The scripts set-up a set of tunnels from local to remote (note that they are reversed
on the opposite side of the link). Then, they run iperf down the tunnel to produce
a bandwidth report.

Optionally, the tunnel may be protected using transport mode IPSEC.

Run on host A

```shell
./test-setup.py --local 192.168.2.114 --remote 192.168.2.105 --subnet 10.0.7 --server

```

Run on host B

```shell
./test-setup.py --local 192.168.2.105 --remote 192.168.2.114 --subnet 10.0.7 --client

```

Then repeat the run with IPSEC transport mode wrap


Run on host A

```shell
./test-setup.py --local 192.168.2.114 --remote 192.168.2.105 --subnet 10.0.7 --server --ipsec

```

Run on host B

```shell
./test-setup.py --local 192.168.2.105 --remote 192.168.2.114 --subnet 10.0.7 --client --ipsec

```

To run a tunnel mode IPSEC test, pass a --config tunnel-tests.json to the ipsec variant of the invocation.

It is possible to see the commands that are going to be executed by passing --dryrun to the script.

The commands and tests are configurable using the tests.json file supplied with the distribution.

Local and Remote IPs must exist on the host. If you want to test a specific NIC use that NIC's IP and set out the routing accordingly. Best of all connect the NICs back-to-back or via a single switch in-between. The test subnet must not conflict and must be specified as in the example - first 3 nibble. The script will set-up sequential /30s in the subnet for the test and tear them down when cleaning up.

