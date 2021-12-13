#!/usr/bin/python3
#pylint: disable=invalid-name
'''Bandwidth tests for tunnel experiments'''

import os
import json
import subprocess
import itertools
from argparse import ArgumentParser

IPSEC="/usr/sbin/ipsec"
CONFIG="tests.json"

class Test():
    '''Simple Test Class'''
    def __init__(self, config):
        conf = open(config, "r")
        parsed = json.load(conf)
        self.tests = parsed["tests"]
        self.ipsec = "\n".join(parsed["ipsec"])
        self.secrets = "\n".join(parsed["secrets"])
        self.common = parsed["common"]
        self.ipsec_id = os.getpid()
        conf.close()

    @staticmethod
    def run_command(command, params, dummy):
        '''Command runner with dry run capability'''
        if dummy:
            print(command.format(**params))
        else:
            subprocess.run(command.format(**params), shell=True, check=False)

    def test_up(self, params, ip_addr=1, dummy=True):
        '''Bring up all tunnels using supplied params'''

        for test in self.tests:
            params["link"] = "{}{}".format(test["name"],self.ipsec_id)
            params["inner"] = params["subnet"] + "." + str(ip_addr)
            if ip_addr % 2 == 0:
                params["inner-remote"] = params["subnet"] + "." + str(ip_addr - 1)
            else:
                params["inner-remote"] = params["subnet"] + "." + str(ip_addr + 1)

            ip_addr = ip_addr + 4

            if dummy:
                print("Test {}".format(test["name"]))
            for command in itertools.chain(test["up"], self.common["up"]):
                self.run_command(command, params, dummy)

    def test_down(self, params, ip_addr=1, dummy=True):
        '''Bring down all tunnels using supplied params'''

        for test in self.tests:
            params["link"] = "{}{}".format(test["name"],self.ipsec_id)
            params["inner"] = params["subnet"] + ".{}".format(ip_addr)

            ip_addr = ip_addr + 4
            for command in itertools.chain(self.common["down"], test["down"]):
                self.run_command(command, params, dummy)

    def ipsec_on(self, params):
        '''Create a temporary ipsec config and enable it'''
        ipsec = open("/etc/ipsec.d/{}.conf".format(self.ipsec_id), "w+")
        params["id"] = self.ipsec_id
        ipsec.write(self.ipsec.format(**params))
        ipsec.close()

        secrets = open("/etc/ipsec.d/{}.secrets".format(self.ipsec_id), "w+")
        secrets.write(self.secrets.format(**params))
        secrets.close()


        subprocess.run("ipsec restart", shell=True, check=False)

    def ipsec_off(self):
        '''Disable the temporary ipsec config'''
        os.unlink("/etc/ipsec.d/{}.conf".format(self.ipsec_id))
        os.unlink("/etc/ipsec.d/{}.secrets".format(self.ipsec_id))
        subprocess.run("ipsec restart", shell=True, check=False)

    def run_server(self):
        '''Run iperf on the server side and record the results'''
        try:
            print("Press Ctrl-C to terminate test")
            #pylint: disable=too-many-format-args
            subprocess.run(
                "iperf -s".format(self.ipsec_id),
                shell=True,
                capture_output=True,
                check=False)
        except KeyboardInterrupt:
            pass

    def run_client(self, params):
        '''Run iperf on the server side and record the results'''

        ip_addr = 1
        #pylint: disable=unused-variable
        print ("Report will be saved in result.{}.txt".format(self.ipsec_id))

        report = open("result.{}.txt".format(self.ipsec_id), "w+")
        for test in self.tests:
            print("Test {}".format(test["name"]))

            source = params["subnet"] + ".{}".format(ip_addr + 1)

            report.write("Test {}\n".format(test["name"]))
            target = params["subnet"] + ".{}".format(ip_addr)
            report.write(subprocess.run(
                "iperf -c {} -B {}".format(target, source),
                shell=True,
                capture_output=True,
                check=False).stdout.decode("utf-8"))
            ip_addr = ip_addr + 4

        report.close()

def main():
    '''Run the test suite'''
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '--config',
        help='Alternative test control config',
        type=str)
    aparser.add_argument(
        '--local',
        help='Local IP address (must exist on this host)',
        required=True,
        type=str)
    aparser.add_argument(
        '--remote',
        help='Remote IP address',
        required=True,
        type=str)
    aparser.add_argument(
        '--subnet',
        help='Subnet for tunnel allocation',
        required=True,
        type=str)
    aparser.add_argument(
        '--server',
        action='store_true',
        help='Run tests as server side')
    aparser.add_argument(
        '--sport',
        default=1702,
        help='EoL2TPv3 default source port')
    aparser.add_argument(
        '--dport',
        default=1702,
        help='EoL2TPv3 default dest port')
    aparser.add_argument(
        '--client',
        action='store_true',
        help='Run tests as client side')
    aparser.add_argument(
        '--ipsec',
        action='store_true',
        help='Run the tests with transport mode IPSEC between local and remote')
    aparser.add_argument(
        '--dryrun',
        action='store_true',
        help='Dry run, do not make any config changes')
    args = vars(aparser.parse_args())

    if (not args.get('server')) and (not args.get('client')):
        raise Exception("Invalid Arguments, no role specified")

    if args.get('server') and args.get('client'):
        raise Exception("Invalid Arguments, only one role at a time")

    Tester = None
    if args.get('config') is not None:
        Tester = Test(args.get('config'))
    else:
        Tester = Test(CONFIG)

    if args.get('ipsec'):
        if args["client"]:
            args["inner"] = args["subnet"] + ".2"
            args["inner-remote"] = args["subnet"] + ".1"
        else:
            args["inner"] = args["subnet"] + ".1"
            args["inner-remote"] = args["subnet"] + ".2"
        Tester.ipsec_on(args)

    if args.get('server'):
        Tester.test_up(args, dummy=args.get('dryrun'))
        Tester.run_server()
    else:
        Tester.test_up(args, ip_addr=2, dummy=args.get('dryrun'))
        Tester.run_client(args)

    Tester.test_down(args, dummy=args.get('dryrun'))
    if args.get('ipsec'):
        Tester.ipsec_off()


if __name__ == '__main__':
    main()
