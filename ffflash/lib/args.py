from argparse import ArgumentParser
from sys import argv as _argv

from ffflash.info import info


def parsed_args(argv=None):
    '''
    Parse arguments from commandline

    :param argv: List of Arguments to parse. - If omitted **sys.argv** is used
    :return Namespace: arguments from **ArgumentParser** for ``argv``
    '''
    parser = ArgumentParser(
        prog=info.name,
        description=info.description,
        epilog=info.ident,
        add_help=True
    )
    parser.add_argument(
        'APIfile', action='store',
        help='Freifunk API File to modify'
    )
    parser.add_argument(
        '-s', '--sidecars', nargs='+',
        help='sync updates from/with sidecar files'
    )
    parser.add_argument(
        '-n', '--nodelist', action='store',
        help='URL or location to map\'s nodelist.json, updates nodes count'
    )
    parser.add_argument(
        '-m', '--meshviewer', action='store',
        help='URL or location to map\'s meshviewer.json, updates nodes count'
    )
    parser.add_argument(
        '-r', '--rankfile', action='store',
        help='location to rankfile.json, for node statistics and credits'
    )
    parser.add_argument(
        '-rc', '--rankclients', action='store', type=float, default=0.01,
        help='factor to increase score per client'
    )
    parser.add_argument(
        '-rf', '--rankoffline', action='store', type=float, default=1.0,
        help='score to decrease on offline'
    )
    parser.add_argument(
        '-rn', '--rankonline', action='store', type=float, default=1.0,
        help='score to increase on online'
    )
    parser.add_argument(
        '-rp', '--rankposition', action='store', type=float, default=0.1,
        help='score to increase on position set'
    )
    parser.add_argument(
        '-rw', '--rankwelcome', action='store', type=float, default=10.0,
        help='score to start with for new nodes'
    )
    parser.add_argument(
        '-d', '--dry', action='store_true',
        help='do not save output, displays only a preview'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='show verbose output'
    )
    parser.add_argument(
        '-D', '--domain', action='store',
        help='filter by subcommunity'
    )

    args = parser.parse_args(
        argv if (argv is not None) else _argv[1:]
    )

    if args.rankfile and not (args.nodelist or args.meshviewer):
        parser.error('argument -r/--rankfile: needs a -n/--nodelist or a -m/--meshviewer')
    return args
