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

It is possible to see the commands that are going to be executed by passing --dryrun to the script.

The commands and tests are configurable using the tests.json file supplied with the distribution.

