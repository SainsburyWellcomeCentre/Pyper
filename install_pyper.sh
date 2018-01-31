#!/usr/bin/env bash

# Download and install anaconda python 2.7 64 bits
# Download and unzip pyper
# cd pyper # assuming the folder is called pyper and we are in the parent folder

# TODO: use json option of conda to parse results

pyper_folder=`pwd`"/pyper"
env_name="pyper_env"

echo "Updating anaconda"
update_log=`conda update -y -q conda`
conda info --envs | grep $env_name
if [ $? -ne 1 ]; then  # Assert that returns empty
    echo "Environemt $env_name already exists, aborting"
    exit
fi
echo "Done."

echo "Creating environment. This may take some time."
env_log=`conda create -y -q -n $env_name python=2.7 anaconda`
source activate $env_name
echo "Done."

echo "Installing dependencies. This may take some time. "
install_log=`conda install -y -q -n pyper_env numpy scipy scikit-image python-dateutil pyparsing matplotlib PyOpenGL progressbar configobj`
install_log=$install_log`conda install -y -q -n pyper_env -c conda-forge ffmpeg opencv=2.4.13.4 pyqt=5.6`
echo "Done."

echo "Installing Pyper."
install_status=`python ./setup.py install`

if [ $? -ne 0 ]; then
    source deactivate
    echo "Installation failed"
else
    source deactivate
    echo "Installation finished"
    echo "To use pyper type the following in a terminal:"
    echo '"source activate pyper_env"'
    # if linux: export GIO_EXTRA_MODULES=/usr/lib/x86_64-linux-gnu/gio/modules/
    echo "and then"
    echo '"python -m pyper.gui.tracking_gui"'
    echo "or"
    echo '"python -m pyper.cli.tracking_cli"'
fi
