REM Download and install anaconda python 2.7 64 bits
REM Download and unzip pyper
REM cd pyper # assuming the folder is called pyper and we are in the parent folder

REM TODO: use json option of conda to parse results

SET pyper_folder=%cd%"\pyper"
REM Make sure the environment does not exist
SET env_name="pyper_env"

echo "Updating anaconda"
conda update -y -q conda
REM Make sure the environment does not exist by hand on windows
REM conda info --envs | grep %env_name%

echo "Creating environment. This may take some time."
conda create -y -q -n %env_name% python=2.7 anaconda
source activate %env_name%
echo "Done."

echo "Installing dependencies. This may take some time. "
conda install -y -q -n pyper_env numpy scipy scikit-image python-dateutil pyparsing matplotlib PyOpenGL progressbar configobj
conda install -y -q -n pyper_env -c conda-forge ffmpeg opencv=2.4.13.4 pyqt=5.6
echo "Done."

echo "Installing Pyper."
python setup.py install
REM assumes success

source deactivate
echo "Installation finished"
echo "To use pyper type the following in a terminal:"
echo '"source activate pyper_env"'
echo "and then"
echo '"python -m pyper.gui.tracking_gui"'
echo "or"
echo '"python -m pyper.cli.tracking_cli"'

