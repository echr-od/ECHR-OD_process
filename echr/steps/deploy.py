#!/bin/python3
import argparse
import os
from sh import osf
import paramiko
import datetime
import sys

from echr.utils.logger import getlogger
from echr.utils.cli import TAB
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
)

log = getlogger()

MAX_RETRY = 3


def get_client(host, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client


def get_password():
    return os.environ.get('ECHR_PASSWORD')


def parse_server_parameters(params_str):
    try:
        params = {e.split('=')[0]: e.split('=')[1] for e in params_str.split()}
        keys = ['user', 'password', 'host', 'folder', 'build', 'workflow']
        in_params = [k in params for k in keys]
        if not all(in_params):
            missing = [keys[i] for i, e in enumerate(in_params) if not e]
            return False, missing
        return True, params
    except:
        return False, []


def runner(params_str, build, title, detach, force, update):
    print(Markdown("- **Step configuration**"))
    ok, params = parse_server_parameters(params_str)
    print(TAB + "> Check server parameters...")
    if not ok:
        if params:
            print(TAB + '  ⮡ [red]:double_exclamation_mark: The following parameters are missing: {}'.format(
                ', '.join(params)))
            return 2
        else:
            print(TAB + '  ⮡ [red]:double_exclamation_mark: Something went wrong')
            return 11
    print(TAB + '  ⮡ [green]:heavy_check_mark: All expected parameters are present')

    print(Markdown("- **Prepare runner**"))
    GIT_REPO = "https://github.com/echr-od/ECHR-OD_process.git"
    DEFAULT_BRANCH = 'develop'
    REPO_PATH = os.path.join(params['folder'], GIT_REPO.split('/')[-1].split('.')[0])

    client = get_client(params['host'], username=params['user'], password=params['password'])

    _, stdout, _ = client.exec_command("[ -d '{}' ] && echo 'exists'".format((params['folder'])), get_pty=True)
    output = stdout.read().decode().strip()
    print(TAB + "> Check if the target folder exists... [green][DONE]")
    if not output:
        cmd = [
            'mkdir -p {}'.format(params['folder']),
        ]
        _, stdout, _ = client.exec_command((';'.join(cmd)))
        print(stdout.read().decode().strip())
        print(TAB + "> Create the target folder... [green][DONE]")
    else:
        print(TAB + "> Target folder already exists... [green][DONE]")
        print(stdout.read().decode().strip())

    _, stdout, _ = client.exec_command("[ -d '{}' ] && echo 'exists'".format((REPO_PATH)), get_pty=True)
    output = stdout.read().decode().strip()
    print(TAB + "> Check if the repository is cloned... [green][DONE]")
    if not output:
        cmd = [
            'cd {}'.format(params['folder']),
            'git clone {}'.format(GIT_REPO)
        ]
        _, stdout, _ = client.exec_command((';'.join(cmd)))
        print(TAB + "> Clone repository... [green][DONE]")
        print(stdout.read().decode().strip())
    else:
        print(TAB + "> Repository already cloned... [green][DONE]")
        print(stdout.read().decode().strip())

    # Fetch and rebase
    cmd = [
        'cd {}'.format(REPO_PATH),
        'git fetch origin {}'.format(params.get('branch', DEFAULT_BRANCH)),
    ]
    _, stdout, _ = client.exec_command((';'.join(cmd)))
    output = stdout.read().decode().strip()
    print(output)
    cmd = [
        'cd {}'.format(REPO_PATH),
        'git rebase origin {}'.format(params.get('branch', DEFAULT_BRANCH))
    ]
    client.exec_command((';'.join(cmd)))
    print(TAB + "> Fetch and rebase the repository... [green][DONE]")

    print(Markdown("- **Execute on runner**"))
    print(TAB + "> Run workflow and detach... [green][DONE]")
    build_str = ""
    if 'build' in params:
        build_str = "--build {}".format(params['build'])
    endpoint_str = ""
    if 'upgrade_endpoint' in params:
        endpoint_str = "--upgrade_endpoint {}".format(params['upgrade_endpoint'])
    cmd = 'tmux new -A -s echr -d "docker run -ti ' \
          '--mount src={},dst=/tmp/echr_process/,type=bind ' \
          'echr_build build --workflow {} {} {}"'.format(REPO_PATH, params['workflow'], build_str, endpoint_str)
    client.exec_command((cmd))


def upload_osf(params_str, build, detach, force, update):
    params = {e.split('=')[0]: e.split('=')[1] for e in params_str.split()}
    dst = params['folder']
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
        for file in files:
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


def upload_scp(params_str, build, detach, force, update):
    params = {e.split('=')[0]: e.split('=')[1] for e in params_str.split()}
    dst = params['folder']
    dst_without_update = os.path.join(dst, 'raw', 'judgments')
    with Progress(
            TAB + "> Retrieving list of files in the project... [IN PROGRESS]\n",
            transient=True,
    ) as progress:
        _ = progress.add_task("Retrieving...")

        client = get_client(params['host'], username=params['user'], password=get_password())
        client.exec_command("du -a {} &> /tmp/list.txt".format((dst_without_update)))
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
            client = get_client(params['host'], username=params['user'], password=get_password())
            cmd = 'mkdir -p {}'.format((dst))
            client.exec_command(cmd)
        print(TAB + "> Creating the destination folder [green][DONE]")

    start = datetime.datetime.now()

    def upload_status(sent, size):
        sent_mb = round(float(sent) / 1000000, 1)
        remaining_mb = round(float(size - sent) / 1000000, 1)
        size_mb = round(size / 1000000, 1)
        time = datetime.datetime.now()
        elapsed = time - start
        if sent > 0:
            remaining_seconds = elapsed.total_seconds() * (float(size - sent) / sent)
        else:
            remaining_seconds = 0
        remaining_hours, remaining_remainder = divmod(remaining_seconds, 3600)
        remaining_minutes, remaining_seconds = divmod(remaining_remainder, 60)

        sys.stdout.write(
            (TAB + "Total size:{0} MB | Sent:{1} MB | Remaining:{2} MB | Time remaining:{3:02}:{4:02}:{5:02}").
                format(
                size_mb, sent_mb, remaining_mb,
                int(remaining_hours), int(remaining_minutes), int(remaining_seconds)))
        sys.stdout.write('\r')

    files = [os.path.join(build, e) for e in ['all.zip', 'datasets.zip']]
    client = get_client(params['host'], username=params['user'], password=get_password())
    for file in files:
        error = ""
        dst_file = file.replace(build, dst + '/')
        if not update or dst_file not in server_files:
            for j in range(MAX_RETRY):
                try:
                    head, _ = os.path.split(dst_file)
                    client.exec_command('mkdir -p {}'.format((head)))
                    sftp = client.open_sftp()
                    sftp.put(file, dst_file, upload_status)
                    break
                except Exception as e:
                    log.debug(e)
    print('\r')
    print(TAB + "> Upload... [green][DONE]\n")

    with Progress(
            TAB + "> Decompress archives... [IN PROGRESS]\n",
            BarColumn(30),
            TimeRemainingColumn(),
            "| ({task.completed}/{task.total}) Uploading [blue]{task.fields[file]} [white]"
            "{task.fields[error]}",
            transient=True,
    ) as progress:
        task = progress.add_task("Decompress...", total=len(files), error="", file=files[0])
        client = get_client(params['host'], username=params['user'], password=get_password())
        for file in files:
            error = ""
            dst_file = file.replace(build, dst + '/')
            for j in range(MAX_RETRY):
                try:
                    head, tail = os.path.split(dst_file)
                    cmd = 'unzip -o "{}"'.format(dst_file)
                    if tail == 'all.zip':
                        cmd += ' -d "{}"'.format(os.path.join(head, '..', '..'))
                    else:
                        cmd += ' -d "{}"'.format(os.path.join(head, tail.split('.')[0]))
                    _, stdout, _ = client.exec_command((cmd))
                    while not stdout.channel.exit_status_ready():
                        if stdout.channel.recv_ready():
                            stdoutLines = stdout.readlines()
                            log.debug(stdoutLines)
                    break
                except Exception as e:
                    print(e)
                    log.debug(e)
                    error = '\n| ({}/{}) Failed to decompress archive {}'.format(
                        j + 1, MAX_RETRY, file)
                    error += '\n| {}'.format(str(e))
                    progress.update(task, advance=0, error=error, file=file)
        progress.update(task, advance=1, error=error, file=file)
    print(TAB + "> Decompress archives... [green][DONE]\n")


def get_list_of_files(build):
    files_list = []
    for path, _, files in os.walk(build):
        for name in files:
            files_list.append(os.path.join(path, name))
    return files_list


def run(console, method, build, params, doc_ids=None, detach=False, force=False, update=False):
    __console = console
    global print
    print = __console.print
    METHODS.get(method)(params, build, detach, force, update)


def main(args):
    console = Console(record=True)
    run(console, args.method, args.build, args.title, args.doc_ids, args.params, args.force, args.update)


def parse_args(parser):
    args = parser.parse_args()
    if args.method not in METHODS.keys():
        print("Invalid method of deployment. Should be among: {}".format(', '.join(METHODS.keys())))
        exit(2)
    return args


METHODS = {
    'osf': upload_osf,
    'scp': upload_scp,
    'runner': runner
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Deploy the dataset')
    parser.add_argument('--build', type=str, default="./build/echr_database/")
    parser.add_argument('--title', type=str)
    parser.add_argument('--doc_ids', type=str, default=None, nargs='+')
    parser.add_argument('--method', type=str, help='Method of deployment among: {}'.format(
        ', '.join(METHODS.keys())))
    parser.add_argument('--params', type=str, help='Parameters for the method')
    parser.add_argument('-f', action='store_true')
    parser.add_argument('-u', action='store_true')
    parser.add_argument('--detach', action='store_true')
    args = parse_args(parser)
    main(args)
