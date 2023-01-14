#!/bin/sh

# invocation:
# cd best-data-review  # as necessary
# . dev/update_environment_yml.sh

if [ -f environment.yml -a -f requirements.txt ]; then
    if conda env export > environment.yml; then
        if pip freeze > requirements.txt; then
            echo "updated environment.yml and requirements.txt"
        else
            echo "could not update requirements.txt"
        fi
    else
        echo "could not update environment.yml"
    fi
else
    echo "Must run this in best-data-review project directory"
fi
