from distutils.core import setup

setup(
    name='pyper',
    version='2.0',
    packages=['pyper', 'pyper.cli', 'pyper.gui', 'pyper.video', 'pyper.camera', 'pyper.config', 'pyper.analysis',
              'pyper.contours', 'pyper.tracking', 'pyper.utilities', 'pyper.exceptions', 'pyper.cv_wrappers', 'tests',
              'tests.test_analysis', 'tests.test_tracking', 'config.plugins'],
    url='https://github.com/SainsburyWellcomeCentre/Pyper',
    license='GPLv2',
    author='Charly Rousseau and Pyper contributors',
    author_email='c.rousseau@ucl.ac.uk',
    description='Motion tracking with closed loop abilities'
)
