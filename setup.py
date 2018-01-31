import sys
import os
import platform
import shutil
import errno
from setuptools import setup, find_packages
from setuptools.command.install import install


SUPPORTED_PYTHON_VERSION = '2.7'

libs_directory = os.path.join(sys.prefix, 'lib', 'python{}'.format(SUPPORTED_PYTHON_VERSION), 'site-packages')
shared_directory = os.path.join(sys.prefix, 'share')  # Where resources should go
global_config_directory = os.path.join(sys.prefix, 'etc', 'pyper')
user_config_dir = os.path.join(os.path.expanduser('~'), '.pyper')


# The following requirements are an indication as the dependencies are installed using conda
requirements = [
    'numpy',
    'scipy',
    'scikit-image',
    'python-dateutil',
    'pyparsing',
    'matplotlib',
    'PyOpenGL',
    'progressbar',
    'configobj',
    # 'ffmpeg',
    # 'opencv=2.4.13.4',
    # 'pyqt=5.6'
]


def mkdir_p(path):
    """
    Make a directory if it does not exist

    :param str path:
    """
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno == errno.EEXIST:
            pass
        else:
            raise err


def filter_exts(src_dir, files, extensions):
    """


    :param str src_dir:
    :param str files:
    :param list extensions:
    :return: list of paths
    """
    return [os.path.join(src_dir, f) for f in files if os.path.splitext(f)[-1] in extensions]


def filter_filenames(src_dir, files, filenames):
    return [os.path.join(src_dir, f) for f in files if f in filenames]


def get_files_list(src_dir, extensions=(), filenames=()):  # TODO: rename
    """

    :param str src_dir:
    :param list extensions:
    :return: list of tuples of the form (directory, [files, in , directory, matching, extension])
    """
    if platform.system() == 'Windows':
        src_dir = src_dir.replace('/', '\\')
    if extensions:
        files_list = [(d, filter_exts(d, files, extensions)) for d, folders, files in os.walk(src_dir)]
    elif filenames:
        files_list = [(d, filter_filenames(d, files, filenames)) for d, folders, files in os.walk(src_dir)]
    else:
        files_list = [(d, [os.path.join(d, f) for f in files]) for d, folders, files in os.walk(src_dir)]
    files_list_no_empty = [pair for pair in files_list if pair[1]]
    return files_list_no_empty


def copy_data(data_list, dest_dir_base, strip_prefix=''):
    """
    Copies the data from data_list as obtained from get_files_list (relatives paths)
    to dest_dir

    :param data_list:
    :param str dest_dir_base:
    :param str strip_prefix:
    :return:
    """

    def left_strip(instr, prefix):
        if not instr.startswith(prefix):
            return instr
        else:
            stripped = instr[len(prefix):]
            # To remove the potential starting / left
            if os.path.isabs(stripped):  # WARNING: May not work on windows
                return stripped[1:]
            else:
                return stripped

    for d, files in data_list:
        dest_dir = os.path.join(dest_dir_base, left_strip(d, strip_prefix))
        print("Creating dir {}".format(dest_dir))
        mkdir_p(dest_dir)
        for f in files:
            dest = os.path.join(dest_dir, os.path.basename(f))  # to strip d and file separator
            print("Copying {} to {}".format(f, dest))
            shutil.copy(f, dest)


def patch_macos_help():
    """
    Necessary patch for MacOS where webkit does not work

    :return:
    """
    if platform.system() == 'Darwin':
        shutil.copy('pyper/qml/help/HelpWindowMacOs', 'pyper/qml/help/pyper/qml/help/')


class CopyResources(install):
    """
    Custom command because setuptools buries the data files in the egg and they are not accessible

    # TODO: add option for doc files & compile doc as option
    """
    def run(self):
        install.run(self)
        # RESOURCES AND QML FILES
        print('\n\n')
        print('Copying data files')
        print('==================')
        pyper_shared_dir = os.path.join(shared_directory, 'pyper')

        qml_files = get_files_list('pyper/qml', ['.qml'])
        qml_files.extend(get_files_list('pyper/qml', extensions=[], filenames=['qmldir']))
        patch_macos_help()
        copy_data(qml_files, pyper_shared_dir, strip_prefix='pyper/')

        icon_files = get_files_list('resources/icons', ['.png'])
        icon_files = [pair for pair in icon_files if 'fullScale' not in pair[0]]
        copy_data(icon_files, pyper_shared_dir)  # Need to be relative to qml files because of qml limitations

        image_files = get_files_list('resources/images', ['.png'])
        copy_data(image_files, pyper_shared_dir)

        videos_files = get_files_list('resources', ['.h264', '.avi'])
        copy_data(videos_files, pyper_shared_dir)

        config_files = get_files_list('config', ['.conf', '.py'])  # Config and Plugins
        copy_data(config_files, global_config_directory, strip_prefix='config')
        copy_data(config_files, user_config_dir, strip_prefix='config')


setup(
    name='pyper',
    version='2.0.0.dev1',
    python_requires='==2.7',
    packages=find_packages(exclude=['config', 'docs', 'tests*']),
    install_requires=requirements,
    # extras_require={
    #     'PDF':  ["ReportLab>=1.2", "RXP"],
    #     'reST': ["docutils>=0.3"],
    # }, e.g. pygments and picamera
    cmdclass={'install': CopyResources},
    # entry_points={
    #     'console_scripts': [
    #         'pyper_cli=pyper:cli:tracking_cli.py',
    #     ],
    # },
    # Use "console_script" entry points to register your script interfaces.
    # You can then let the toolchain handle the work of turning these interfaces into actual scripts [2].
    # The scripts will be generated during the install of your distribution.
    download_url='git+git://github.com/SainsburyWellcomeCentre/Pyper',
    url='https://github.com/SainsburyWellcomeCentre/Pyper',
    license='GPLv2',
    author='Charly Rousseau and Pyper contributors',
    author_email='Charly Rousseau <c.rousseau@ucl.ac.uk>',
    description='Motion tracking with closed loop abilities',
    classifiers=['Development Status :: 4 - Beta',  # TODO: change for release
                 'Programming Language :: Python :: 2.7',
                 'Environment :: Console',
                 'Environment :: MacOS X',
                 'Environment :: Win32 (MS Windows)',
                 'Environment :: X11 Applications :: Qt',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Science/Research',
                 'Natural Language :: English',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX :: Linux',
                 'Topic :: Scientific/Engineering :: Image Recognition'
                 ]
)
