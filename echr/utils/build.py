import os
import shutil
import yaml
from pathlib import Path
from datetime import datetime
from rich.markdown import Markdown

from echr.utils.config import config
from echr.utils.cli import TAB
from echr.utils.logger import getlogger
from echr.utils.misc import get_from_path

log = getlogger()


def parse_argument(arg, cli_args):
    if arg.startswith('$'):
        var_name = arg[1:]
        env_var = os.environ.get(var_name)
        if env_var:
            return env_var, 1

        cli_var = vars(cli_args).get(var_name.lower())
        if cli_var:
            return cli_var, 2

        config_var = get_from_path(config(), 'build.env.{}'.format(var_name))
        if config_var:
            return config_var, 3

        if var_name in globals():
            return globals()[var_name], 4

        if var_name == 'MAX_DOCUMENTS':
            return -1, 4

        return arg, -1
    else:
        return arg, 0

def parse_workflow(console, steps_names, workflow, workflow_path, actions_path):
    parsed_workflow = []
    parsed_workflow_steps_names = steps_names
    available_actions = [f.split('.')[0] for f in os.listdir(actions_path) if
                         os.path.splitext(f)[1] in ['.yaml', '.yml']]
    available_workflows = [f.split('.')[0] for f in os.listdir(workflow_path) if
                           os.path.splitext(f)[1] in ['.yaml', '.yml']]
    for e in workflow.get('steps', []):
        if e.get('type') == 'action':
            action_name = e.get('run')
            if action_name not in available_actions:
                console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Workflow is invalid. '
                                    'Action {} does not exist.'.format(action_name))
                exit(1)
            if action_name not in parsed_workflow_steps_names:
                try:
                    with open(os.path.join(actions_path, '{}.yml'.format(action_name))) as f:
                        action = yaml.load(f, Loader=yaml.FullLoader)
                        parsed_workflow.append(action)
                        parsed_workflow_steps_names.append(action_name)
                except Exception as e:
                    console.print_exception()
                    log.error(e)
                    console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: '
                                        'Could not properly load the action {}!'.format(action_name))
                    exit(1)
        elif e.get('type') == 'workflow':
            workflow_name = e.get('run')
            if workflow_name not in available_workflows:
                console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Workflow {} does not exist. '
                                    'Available workflows are: {}'.format(workflow_name, ', '.join(available_workflows)))
                exit(1)
            try:
                with open(os.path.join(workflow_path, '{}.yml'.format(workflow_name))) as f:
                    new_workflow = yaml.load(f, Loader=yaml.FullLoader)
                    parsed_workflow += parse_workflow(console, parsed_workflow_steps_names, new_workflow, workflow_path, actions_path)
            except Exception as e:
                console.print_exception()
                log.error(e)
                console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: '
                                    'Could not properly load the workflow {}!'.format(workflow_name))
                exit(1)
        else:
            console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Workflow is invalid. '
                                'Type {} does not exist.'.format(e.get('type')))
            exit(1)
    return parsed_workflow

def load_workflow(console, args):
    WORKFLOW_PATH = './workflows'
    ACTION_PATH = os.path.join(WORKFLOW_PATH, 'actions')
    workflow = args.workflow
    workflow_steps = []
    console.print(TAB + '> Workflow to execute: [bold black on green]{}'.format(workflow.upper()))
    if os.path.isdir(WORKFLOW_PATH):
        available_workflows = [f.split('.')[0] for f in os.listdir(WORKFLOW_PATH) if
                               os.path.splitext(f)[1] in ['.yaml', '.yml']]
        if workflow not in available_workflows:
            console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Workflow {} does not exist. '
                          'Available workflows are: {}'.format(workflow, ', '.join(available_workflows)))
            exit(1)
        else:
            try:
                with open(os.path.join(WORKFLOW_PATH, '{}.yml'.format(workflow))) as f:
                    workflow_steps = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as e:
                console.print_exception()
                log.error(e)
                console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Could not properly load the workflow!')
                exit(1)
            console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully loaded workflow "{}"'.format(workflow))
            log.info(workflow_steps)
    else:
        console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Workflow folder does not exist!')
        exit(1)

    console.print(TAB + '> Parse workflow')
    workflow_steps = parse_workflow(console, [], workflow_steps, WORKFLOW_PATH, ACTION_PATH)

    console.print(TAB + '> Replace workflow variables')
    all_replaced = True
    try:
        for i, step in enumerate(workflow_steps):
            for arg in step.get('args', {}):
                val, rc = parse_argument(str(step['args'][arg]), cli_args=args)
                if rc != 0:
                    workflow_steps[i]['args'][arg] = val
                    if rc < 0:
                        console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: STEP{}.{}={}'.format(i, arg, val))
                        all_replaced = False
    except Exception as e:
        console.print_exception()
        log.error(e)
        console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Could not replace workflow variables')
        exit(1)

    if not all_replaced:
        console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Could not replace all workflow variables')
        exit(1)
    else:
        console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully replaced workflow variables')

    return workflow_steps


def prepare_build_folder(console, args):
    build = args.build
    force = args.force
    update = False
    console.print(TAB + '> Build folder: {}'.format(build))
    create_build_folder = False
    if os.path.isdir(build):
        if args.strict and not args.force:
            console.print(TAB + "  ⮡ [bold red]:double_exclamation_mark: Build folder exists.")
            console.print(TAB + "    [bold red] > Select another folder or delete the previous build")
            exit(1)
        elif not args.force:
            console.print(TAB + '  ⮡ [bold blue]! Build folder exists. The build will be UPDATED.')
            console.print(TAB + "    [bold yellow]:warning: If you don't want to update the build, use --force flag")
            update = True
        elif args.force:
            console.print(TAB + '  ⮡ [bold blue]! Build folder exists. The build will be RECREATED.')
            try:
                shutil.rmtree(build)
            except OSError as e:
                console.print_exception()
                log.error(e)
                console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Deletion of the build directory {} failed'.format(
                    build))
                exit(1)
            else:
                console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully deleted the directory {}'.format(build))
                create_build_folder = True
    else:
        create_build_folder = True

    if create_build_folder:
        try:
            Path(build).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print_exception()
            log.error(e)
            console.print(
                TAB + '  ⮡ [bold red]:double_exclamation_mark: Creation of the build directory {} failed'.format(build))
            exit(1)
        else:
            console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully created the directory {}'.format(build))

    return force, update


def prepare_logs(console, args):
    log_folder = config().get('logging', {}).get('log_folder')
    log_file = config().get('logging', {}).get('build_log_file')
    log_path = os.path.join(log_folder, log_file)
    console.print(TAB + '> General log file: {}'.format(log_path))
    if not os.path.isdir(log_folder):
        try:
            Path(log_folder).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print_exception()
            log.error(e)
            console.print(
                TAB + '  ⮡ [bold red]:double_exclamation_mark: Creation of the general log directory {} failed'.format(
                    log_path))
            exit(1)
        else:
            console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully created the log directory {}'.format(log_path))

    build_log_path = os.path.join(args.build, 'logs')
    console.print(TAB + '> Build log folder: {}'.format(build_log_path))
    if not os.path.isdir(build_log_path):
        try:
            Path(build_log_path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print_exception()
            log.error(e)
            console.print(TAB + '  ⮡ [bold red]:double_exclamation_mark: Creation of the build log directory {} failed'.format(
                build_log_path))
            exit(1)
        else:
            console.print(
                TAB + '  ⮡ [green]:heavy_check_mark: Successfully created the build log directory {}'.format(build_log_path))
    return log_folder

def place_lock(console, build='./build', name='.lock'):
    token_path = os.path.join(build, name)
    if os.path.isfile(token_path):

        console.print(
            TAB + '  ⮡ [bold red]:double_exclamation_mark: A lock file already exists: {}'.format(
                token_path))
        exit(1)
    else:
        with open(token_path, 'w'): pass
        console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully placed the lock')

def remove_lock(console, build='./build', name='.lock'):
    token_path = os.path.join(build, name)
    if os.path.isfile(token_path):
        try:
            os.remove(token_path)
            console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully removed the lock')
        except:
            pass


def append_history(workflow, build='./build', name='.build_history'):
    history_path = os.path.join(build, name)
    now = datetime.now()
    date_time = now.strftime("%Y/%m/%d %H:%M:%S")
    with open(history_path, 'a+') as f:
        f.write('{}::{}\n'.format(date_time, workflow))


def prepare_build(console, args):
    console.print(Markdown("- **Check the build configuration**"))
    console.print(TAB + '> Number of documents to retrieve:')
    if args.max_documents is None:
        console.print(
            TAB + '  ⮡ [bold blue]! No maximum number of documents specified, the number of documents to retrieve will be automatically determined.')
    else:
        console.print(TAB + '  ⮡ [bold blue]! Database will be built with a maximum number of {} documents'.format(
            args.max_documents))

    workflow = load_workflow(console, args)
    force, update = prepare_build_folder(console, args)
    place_lock(console)
    build_log_path = prepare_logs(console, args)
    return workflow, build_log_path, update, force