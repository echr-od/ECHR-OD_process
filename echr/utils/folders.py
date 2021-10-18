import os
import shutil
from echr.utils.logger import getlogger
from echr.utils.cli import TAB

LOG_FOLDER = './logs'
LOG_PATH = os.path.join(LOG_FOLDER, 'build.log')
log = getlogger(logfile_path=LOG_PATH)


def make_build_folder(console, full_path, force=False, strict=False):
    create_folder = False
    if os.path.isdir(full_path):
        if strict and not force:
            console.print(TAB + "  ⮡ [bold red]:double_exclamation_mark: Step folder exists.")
            console.print(TAB + "    [bold red] > Select another folder or delete the previous build")
            exit(1)
        elif not force:
            console.print(TAB + '  ⮡ [bold blue]! Step folder exists. The build will be UPDATED.')
            console.print(TAB + "    [bold yellow]:warning: If you don't want to update the build, use --force flag")
        elif force:
            console.print(TAB + '  ⮡ [bold blue]! Step folder exists. The build will be RECREATED.')
            try:
                shutil.rmtree(full_path)
            except OSError as e:
                log.debug(e)
                console.print(
                    TAB + '  ⮡ [bold red]:double_exclamation_mark: Deletion of the step directory {} failed'.format(
                        full_path))
                exit(1)
            else:
                console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully deleted the directory {}'.format(
                    full_path))
                create_folder = True
    else:
        create_folder = True

    if create_folder:
        try:
            os.makedirs(full_path, exist_ok=True)
        except Exception as e:
            console.print_exception()
            log.error(e)
            console.print(
                TAB + '  ⮡ [bold red]:double_exclamation_mark: Could not create step directory: {}'.format(
                    full_path))
            exit(1)
        console.print(TAB + '  ⮡ [green]:heavy_check_mark: Successfully created the directory {}'.format(full_path))
