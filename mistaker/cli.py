# mistaker/cli.py
import csv
import sys
import io
import argparse
from . import Generator, __version__


def process_file(generator: Generator, input_path: str):
    """Process input CSV file and write results to stdout"""
    output_wrapper = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", newline="", write_through=True
    )

    try:
        with open(input_path, "r", newline="") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV file has no headers")

            writer = csv.DictWriter(output_wrapper, fieldnames=reader.fieldnames)
            writer.writeheader()

            # Process all records through the generator
            for record in generator.generate_all(reader):
                writer.writerow(record)

    except BrokenPipeError:
        # Handle case where output is piped to head or similar
        sys.stderr.close()
    finally:
        # Don't close stdout
        output_wrapper.detach()


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic data with realistic mistakes"
    )
    parser.add_argument(
        "input_file", nargs="?", default="-", help="Input CSV file (use - for stdin)"
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Configuration JSON file path (defaults to ./config.json if exists)",
    )
    parser.add_argument(
        "--min-duplicates", type=int, help="Minimum number of variations per record"
    )
    parser.add_argument(
        "--max-duplicates", type=int, help="Maximum number of variations per record"
    )
    parser.add_argument(
        "--min-chaos", type=int, help="Minimum number of mistakes per field"
    )
    parser.add_argument(
        "--max-chaos", type=int, help="Maximum number of mistakes per field"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    try:
        # Create generator with defaults or from config file if specified
        generator = Generator.from_file(args.config)

        # Override with command line arguments if provided
        if args.min_duplicates is not None:
            generator.config["min_duplicates"] = args.min_duplicates
        if args.max_duplicates is not None:
            generator.config["max_duplicates"] = args.max_duplicates
        if args.min_chaos is not None:
            generator.config["min_chaos"] = args.min_chaos
        if args.max_chaos is not None:
            generator.config["max_chaos"] = args.max_chaos

        # Revalidate config after changes
        generator.validate_config()

        # Handle stdin or file input
        if args.input_file == "-":
            if sys.stdin.isatty():
                parser.print_help()
                return 1
            process_file(generator, sys.stdin)
        else:
            process_file(generator, args.input_file)

    except FileNotFoundError as e:
        print(f"Error: Could not find file '{e.filename}'", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
