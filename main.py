import argparse
import sys

from services.config import delete_config, run_interactive_config_builder
from services.job import Job, run_interactive_job_builder
from services.text_processing import read_and_chunk_text


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="Vocalbook CLI",
        description="A command line interface for interacting with Vocalbook",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- create-config ---
    create_config_parser = subparsers.add_parser(
        "create-config", help="Create a new voice config"
    )

    # --- delete-config ---
    delete_config_parser = subparsers.add_parser(
        "delete-config", help="Deletes a config from the config file"
    )
    delete_config_parser.add_argument("-n", "--config-name", type=str, required=True)

    # --- create-job ---
    job_parser = subparsers.add_parser("create-job", help="Create a new job")

    # --- delete-job ---
    delete_job_parser = subparsers.add_parser(
        "delete-job", help="Deletes a job from the job file"
    )
    delete_job_parser.add_argument("-n", "--job-name", type=str, required=True)

    # --- run-job ---
    run_job_parser = subparsers.add_parser("run-job", help="Runs the job")
    run_job_parser.add_argument("-n", "--job-name", type=str, required=True)

    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)

    if args.command == "create-config":
        run_interactive_config_builder()
    elif args.command == "delete-config":
        config_name = args.config_name
        delete_config(config_name)
    elif args.command == "create-job":
        run_interactive_job_builder()
    elif args.command == "delete-job":
        job = Job(args.job_name)
        job.delete_job()
    elif args.command == "run-job":
        job = Job(args.job_name)
        job.run_job()


if __name__ == "__main__":
    main(sys.argv[1:])
