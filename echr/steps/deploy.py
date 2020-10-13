#!/bin/python3
import argparse
import os
from sh import osf, scp
import paramiko
import shutil

from echr.utils.logger import getlogger
from echr.utils.cli import TAB
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
)
log = getlogger()

MAX_RETRY = 3

def get_password():
    return os.environ.get('ECHR_PASSWORD')

def detach_osf(params_str, build, dst, detach, force, update):
    params = {e.split('=')[0]: e.split('=')[1] for e in params_str.split()}

    cmd = '/usr/bin/nohup sh -c "cd {}; docker run --env ECHR_PASSWORD={} -ti ' \
          '--mount src=$(pwd),dst=/tmp/echr_process/,type=bind echr_build build ' \
          '--workflow deploy_to_OSF" &'.format(params['folder'], os.environ.get('ECHR_PASSWORD'))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(params['host'], username=params['user'], password=params['password'])
    client.exec_command(cmd)


def upload_osf(params_str, build, dst, force, update):
    params = {e.split('=')[0]: e.split('=')[1] for e in params_str.split()}

    with Progress(
            TAB + "> Retrieving list of files in the project... [IN PROGRESS]\n",
            transient=True,
    ) as progress:
        _ = progress.add_task("Retrieving...")
        osf_files = osf('-p', params['project'], '-u', params['user'], 'ls', _env={'OSF_PASSWORD': get_password()})
    print(TAB + "> Retrieving list of files in the project... [green][DONE]\n")

    osf_files = [f.replace('osfstorage/', '').strip() for f in osf_files]
    files = get_list_of_files(build)
    with Progress(
        TAB + "> Uploading... [IN PROGRESS]\n",
        BarColumn(30),
        TimeRemainingColumn(),
        "| ({task.completed}/{task.total}) Uploading [blue]{task.fields[file]} [white]"
        "{task.fields[error]}",
        transient=True,
    ) as progress:
        task = progress.add_task("Uploading...", total=len(files), error="", file=files[0])
        for i, file in enumerate(files):
            error = ""
            dst_file = file.replace(build, dst + '/')
            if not update or dst_file not in osf_files:
                for j in range(MAX_RETRY):
                    try:
                        osf('-p', params['project'], '-u', params['user'], 'upload', '-f', file, dst_file,
                            _env={'OSF_PASSWORD': get_password()})
                        break
                    except Exception as e:
                        log.debug(e)
                        error = '\n| ({}/{}) Failed to upload document {}'.format(
                            j + 1, MAX_RETRY, file)
                        error += '\n| {}'.format(str(e))
                        progress.update(task, advance=0, error=error, file=file)
            else:
                error = "\n| Skip as document exists already"
            progress.update(task, advance=1, error=error, file=file)
    print(TAB + "> Upload... [green][DONE]\n")


def upload_scp(params_str, build, dst, detach, force, update):
    params = {e.split('=')[0]: e.split('=')[1] for e in params_str.split()}
    with Progress(
            TAB + "> Retrieving list of files in the project... [IN PROGRESS]\n",
            transient=True,
    ) as progress:
        _ = progress.add_task("Retrieving...")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(params['host'], username=params['user'], password=get_password())
        client.exec_command("du -a {} &> /tmp/list.txt".format(dst))
        sftp = client.open_sftp()
        sftp.get('/tmp/list.txt', '/tmp/list.txt')
        with open('/tmp/list.txt', 'r') as f:
            files_list = f.readlines()
        server_files = [f.split('\t')[-1].strip() for f in files_list]
    print(TAB + "> Retrieving list of files in the project... [green][DONE]")

    if 'No such file or directory' in server_files[0]:
        with Progress(
            TAB + "> Creating the destination folder [IN PROGRESS]\n",
            transient=True,
        ) as progress:
            _ = progress.add_task("Creating...")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(params['host'], username=params['user'], password=get_password())
            client.exec_command('mkdir -p {}'.format(dst))
        print(TAB + "> Creating the destination folder [green][DONE]")


    files = get_list_of_files(build)
    with Progress(
        TAB + "> Uploading... [IN PROGRESS]\n",
        BarColumn(30),
        TimeRemainingColumn(),
        "| ({task.completed}/{task.total}) Uploading [blue]{task.fields[file]} [white]"
        "{task.fields[error]}",
        transient=True,
    ) as progress:
        task = progress.add_task("Uploading...", total=len(files), error="", file=files[0])
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(params['host'], username=params['user'], password=get_password())
        for i, file in enumerate(files):
            error = ""
            dst_file = file.replace(build, dst + '/')
            if not update or dst_file not in server_files:
                for j in range(MAX_RETRY):
                    try:
                        head, _ = os.path.split(dst_file)
                        client.exec_command('mkdir -p {}'.format(head))
                        sftp = client.open_sftp()
                        sftp.put(file, dst_file)
                        break
                    except Exception as e:
                        log.debug(e)
                        error = '\n| ({}/{}) Failed to upload document {}'.format(
                            j + 1, MAX_RETRY, file)
                        error += '\n| {}'.format(str(e))
                        progress.update(task, advance=0, error=error, file=file)
            else:
                error = "\n| Skip as document exists already"
            progress.update(task, advance=1, error=error, file=file)
    print(TAB + "> Upload... [green][DONE]\n")


def get_list_of_files(build):
    files_list = []
    folders = ['structured', 'unstructured', 'logs']
    for folder in folders:
        for path, subdirs, files in os.walk(os.path.join(build, folder)):
            for name in files:
                files_list.append(os.path.join(path, name))
    return files_list

def run(console, method, build, dst, params, detach=False, force=False, update=False):
    __console = console
    global print
    print = __console.print

    METHODS.get(method)(params, build, dst, detach, force, update)

def main(args):
    console = Console(record=True)
    run(console, args.method, args.build, args.dst, args.params, args.force, args.update)


def parse_args(parser):
    args = parser.parse_args()
    if args.method not in METHODS.keys():
        print("Invalid method of deployment. Should be among: {}".format(', '.join(METHODS.keys())))
        exit(2)
    # Check path
    return args

METHODS = {
    'osf': upload_osf,
    'scp': upload_scp,
    'detach_osf': detach_osf
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy the dataset')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--dst', type=str, help='Destination folder')
    parser.add_argument('--method', type=str, help='Method of deployment among: {}'.format(
        ', '.join(METHODS.keys())))
    parser.add_argument('--params', type=str, help='Parameters for the method')
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    parser.add_argument('--detach', action='store_true')
    args = parse_args(parser)
    main(args)
