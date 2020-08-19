#!/bin/bash

function display_help {
    echo 'USAGE:'
    echo 'docker run -ti [--rm] --mount source=$(pwd)/src,destination=/tmp/echr_process,type=bind,readonly <image_id|image_name[:image_tag]> [help | bash | /bin/bash | deploy | build | pytest [pytest options] [file_or_dir] [...] | lint | all]'
    echo
    echo 'OPTIONS:'
    echo '  help              - Prints this help and exits.'
    echo '  bash | /bin/bash  - Allows to access bash console of the container.'
    echo '  deploy            - Deploy a build to a given server'
    echo '  all               - Runs pytest'
    echo '                    - Then, build ECHR database'
    echo '                      After all, check the data.'
    echo '  test              - Runs pytest.'
    echo '  build             - Build ECHR database.'
    echo '  lint              - Runs pylint.'
}

function display_mounting_error {
    echo "Mount echr_process directory into /tmp/echr_process in order to run test process properly."
    echo "Use the following snippet in docker run command:"
    echo '--mount src="$(pwd)"/src,dst=/tmp/echr_process/src,type=bind,readonly\n'
}

function build {
  python3 ./build.py ${@:2}
}

function deploy {
  echo "non-implemented yet :)"
}

function lint_source_code {
    python -m pylint --rcfile=.pylintrc ./*.py
}

function handle_input {
    if [[ "$#" -eq 0 ]] ; then
        display_help
    else
        if [[ "$1" = 'bash' || "$1" = '/bin/bash' ]] ; then
            /bin/bash
        elif [[ "$1" = "build" ]] ; then
          build $@
        elif [[ "$1" = "all" ]] ; then
            python -m pytest -v -c ./.pytest.ini --disable-warnings &&\
            lint_source_code
        elif [[ "$1" = "test" ]] ; then
            python -m pytest -v -c ./.pytest.ini --disable-warnings
        elif [[ "$1" = 'lint' ]] ; then
            lint_source_code
        else
          display_help
        fi
    fi
}

function main() {
    handle_input $@
    status_code=$?
    exit ${status_code}
}

main $@