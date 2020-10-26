#!/bin/python3
import subprocess
import argparse
import importlib
from datetime import datetime
import os
import signal
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from echr.utils.build import prepare_build, remove_lock, append_history
from echr.utils.cli import strfdelta, TAB
from echr.utils.logger import getlogger, serialize_console_logs

OSF_DST = 'test'
BUILD_PATH = './build'
OSF_PARAMS = 'user=alexandre.quemy@gmail.com project=52rhg'

LOG_FOLDER = './logs'
LOG_PATH = os.path.join(LOG_FOLDER, 'build.log')
log = getlogger(logfile_path=LOG_PATH)

console = Console(record=True)
print = console.print  # Redefine print

LIMIT_TOKENS = 10000

signal.signal(signal.SIGINT, signal.default_int_handler)

def main(args):
    global console
    global print
    if args.no_tty:
        file = open(os.path.join(BUILD_PATH, 'run.log'), 'w')
        console = Console(record=True, file=file)
        print = console.print  # Redefine print

    print(Panel.fit('[bold yellow] :scales: {} :scales: '.format(
            "European Court of Human Rights Open Data Building Process".upper()), ), justify="center")

    workflow_steps, build_log_path, update, force = prepare_build(console, args)

    def execute_step(step, build, args, title, index=None, chrono=True):
        if index:
            print(Panel('[bold yellow] {}'.format(title.upper()), title='STEP {}.'.format(index)))
        else:
            print(Panel('[bold yellow] {}'.format(title)))
        step_start_time = datetime.now()
        step.run(console=console, build=build, **args)
        step_stop_time = datetime.now()
        if chrono:
            step_delta = step_stop_time - step_start_time
            print('\n[blue]🕑 Step executed in {}'.format(strfdelta(step_delta, "{hours}h {minutes}min {seconds}s")))

    start_time = datetime.now()
    for i, step_info in enumerate(workflow_steps):
        step_args = step_info.get('args', {})
        if step_info.get('updatable', False) and update:
            step_args['update'] = True
        if force:
            step_args['force'] = True

        step_executor = importlib.import_module(step_info.get('run'))
        execute_step(
            step=step_executor,
            build=args.build,
            args=step_args,
            title=step_info.get('title', 'Untitled'),
            index=i
        )
    stop_time = datetime.now()
    step_delta = stop_time - start_time
    print('\n[blue]🕑 Building process executed in {}'.format(strfdelta(step_delta, "{hours}h {minutes}min {seconds}s")))

    print(Panel('[bold yellow] POST BUILD STEP'))

    print(Markdown("- **Post build cleaning**"))
    print(TAB + '> Serialize console logs')
    build_log_path = os.path.join(args.build, 'logs')
    serialize_console_logs(console, filename='build', path=build_log_path)

    print(TAB + '> Append build run to build history')
    append_history(args.workflow)

    print(TAB + '> Remove lock file')
    remove_lock(console)


def parse_args(parser):
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate the whole database')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('-s', '--strict', action='store_true')
    parser.add_argument('--no-tty', action='store_true')
    parser.add_argument('--max_documents', type=int, help='Maximum number of documents to retrieve')
    parser.add_argument('--params', type=str, help='Additional parameters to override workflow parameters')
    parser.add_argument('-w', '--workflow', type=str, default='local', help='Workflow to execute')

    args = parse_args(parser)
    try:
        main(args)
    except KeyboardInterrupt:
        remove_lock(console)