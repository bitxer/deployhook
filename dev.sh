#!/bin/bash

trap cleanup SIGINT SIGTERM SIGKILL

cleanup() {
    # If virtual environment is activated, deactivate it.
    command -v deactivate >/dev/null 2>&1 && deactivate
    rm -rf /tmp/test-*
    find ./hook/ -type d -name __pycache__ -exec rm -r {} \+
    find ./tests/ -type d -name __pycache__ -exec rm -r {} \+
    echo "[*] Exiting..."
    exit
}

# Change to the correct directory.
cd "$(dirname "$0")"
HOOK_DIR=$(pwd)
echo "[*] Working in: ${HOOK_DIR}"
git clone https://github.com/bitxer/deployhook-test-github.git /tmp/test-github
git clone https://gitlab.com/bitxer/deployhook-test-gitlab.git /tmp/test-gitlab
export REPO_CONFIG_FILE=tests/config.ini

while getopts tcrd: OPTION; do
    case "${OPTION}" in
        t)
        TESTING="yes"
        break
        ;;
        c)
        CLEAN_SET="yes"
        if [[ -d "./APPDATA/dev" ]]; then
            rm -rf ./APPDATA/dev/logs/*
        fi
        ;;
    esac
done

echo "=================================================="
echo "[!] WARNING:"
echo "[!] This script is only intended for development use. Production use is NOT SUPPORTED!"
echo "=================================================="
sleep 2

# Some default exports.
export REVERSEPROXY="no"
export SECURE="no"
if [[ -f "/etc/timezone" ]]; then
    export TZ=$(cat /etc/timezone)
else
    # Set default as Asia/Singapore.
    export TZ="Asia/Singapore"
fi

# Install Virtual Environment for use
python3 -m pip install virtualenv

if [[ -z "${TESTING}" ]]; then
    if [[ -z "${CLEAN_SET}" ]]; then
        if [[ -d "./APPDATA/dev" ]]; then
            while true; do
                read -p "Remove old logs? [Y/n] : " CLEAN_IN
                case "${CLEAN_IN}" in
                    [Yy])
                    # Remove old data.
                    rm -rf ./APPDATA/dev/logs/*
                    break
                    ;;
                    [Nn])
                    break
                    ;;
                    *)
                    echo "[!] Invalid input detected."
                    ;;
                esac
            done
        fi
    fi

    mkdir -p ./APPDATA/dev/logs

    export LOG_FOLDER=${HOOK_DIR}/APPDATA/dev/logs

    if [[ ! -d ./APPDATA/dev/venv ]]; then
        virtualenv -p python3 ./APPDATA/dev/venv
    fi

    # Activate Python virtual environment.
    . ./APPDATA/dev/venv/bin/activate
    python3 -m pip install --no-cache-dir -r ./requirements.txt | grep -v "Requirement already satisfied"

    python3 dev.py

    # Delete cache.
    echo "[*] Cleaning cache..."
    rm -rf ./APPDATA/dev/cache/*
    cleanup
else
    # Run tests.
    echo "[+] Running Tests."
    echo ""

    if [[ -d "./APPDATA/tests" ]]; then
        rm -rf ./APPDATA/tests/logs
    fi
    mkdir -p ./APPDATA/tests/logs

    export LOG_FOLDER=${HOOK_DIR}/APPDATA/tests/logs
    if [[ ! -d ./APPDATA/tests/venv ]]; then
        virtualenv -p python3 ./APPDATA/tests/venv
    fi

    # Activate Python virtual environment.
    . ./APPDATA/tests/venv/bin/activate
    python3 -m pip install --no-cache-dir -r ./requirements.txt | grep -v "Requirement already satisfied"

    nose2 -v -s tests/ -t .

    # Delete cache.
    echo "[*] Cleaning cache..."
fi

# Deactivate virtual environment and cleanup residue.
cleanup
