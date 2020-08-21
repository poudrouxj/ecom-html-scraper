from scraper.run import run_scraper
import json
import argparse

def main(args):
    run_scraper(args)

if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(
        description='json file with configuration arguments provided at run time from the CLI'
    )
    cli_parser.add_argument(
        '-c',
        '--config_file',
        dest='config_file',
        type=str,
        default=None,
        help='config file',
    )

    args, unknown = cli_parser.parse_known_args()
    parser = argparse.ArgumentParser(parents=[cli_parser], add_help=False)

    if args.config_file is not None:
        if '.json' in args.config_file:
            config = json.load(open(args.config_file))
            parser.set_defaults(**config)

        args = parser.parse_args()

    main(vars(args))