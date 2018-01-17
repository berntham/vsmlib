import sys
import argparse


class CLI(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='VSMlib commad line interface',
            usage='''vsmlib <command> [<args>]

The most commonly used vsmblib commands are:
   benchmark        Record changes to the repository
   create_vocab     Create vocabulary from a folder
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def benchmark(self):
        parser = argparse.ArgumentParser(
            description='Record changes to the repository')
        # prefixing the argument with -- means it's optional
        parser.add_argument('--amend', action='store_true')
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        from vsmlib.benchmarks.evaluate_all import main as main_eval
        main_eval(sys.argv[2:])

    def create_vocab(self):
        print("CLI not implemented yet")


def main():
    CLI()


if __name__ == '__main__':
    main()
