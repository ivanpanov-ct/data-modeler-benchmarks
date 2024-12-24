#!/usr/bin/env python3

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Data modeler evaluator CLI."
    )
    
    # Create subparsers for different subcommands (e.g., `fetch`, `process`, `save`).
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    
    # Subcommand: fetch
    full_auto_parser = subparsers.add_parser("auto", help="run evaluation fully automated (AI will match expected the real output with expected on)")
    # fetch_parser.add_argument("-u", "--url", required=True, help="API endpoint URL")
    
    # Subcommand: process
    human_parser = subparsers.add_parser("human", help="run human evaluation (every generated output will be shown to human along with the expected output. Human will give a score to generated output)")
    
    # Subcommand: save
    save_parser = subparsers.add_parser("hybrid", help="run human + AI evaluation (every generated output along with the expected output will be shown to AI. If it obviously matches, AI gives it a high score. Otherwise it will be given to a human for evaluation)")
    
    # Parse the args and dispatch to the appropriate handler
    args = parser.parse_args()
    
    if args.command == "auto":
        handle_full_auto(args)
    elif args.command == "human":
        handle_human(args)
    elif args.command == "hybrid":
        handle_hybrid(args)
    else:
        parser.print_help()
        sys.exit(1)


def handle_full_auto(args):
    """Handler for the 'auto' command."""
    url = args.url
    try:
        print("Data fetched successfully!")
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")


def handle_human(args):
    """Handler for the 'human' command."""
    input_path = args.input
    try:
        print("Data processed. Here's a preview:")
        print(processed_data[:100])  # show first 100 chars
    except Exception as e:
        print(f"Error processing file {input_path}: {e}")


def handle_hybrid(args):
    """Handler for the 'save' command."""
    output_path = args.output
    # For demonstration, let's just save a mock string
    data_to_save = "Hello, world! This is some data to save."
    try:
        file_utils.write_file(output_path, data_to_save)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error saving data to {output_path}: {e}")


if __name__ == "__main__":
    main()
