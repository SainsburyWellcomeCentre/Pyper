import os, sys
from configobj import ConfigObj

global_config_directory = os.path.join(sys.prefix, 'etc', 'pyper')
user_config_dir = os.path.join(os.path.expanduser('~'), '.pyper')
shared_directory = os.path.join(sys.prefix, 'share', 'pyper')  # Where resources should go

conf_file_name = 'pyper.conf'

# The config will be read with this priority
config_dirs = [
    os.path.join(user_config_dir, conf_file_name),
    global_config_directory,
    'config',  # WARNING: relies on working directory
    '../config',  # For sphinx doc  # TODO: add check that run by sphinx
]

config_path = None
for d in config_dirs:
    p = os.path.join(d, conf_file_name)
    if not os.path.exists(p):
        continue
    else:
        config_path = p
        break

# TODO: add exception handling if config_path is None

config = ConfigObj(config_path, encoding="UTF8", indent_type='    ', unrepr=True,
                   create_empty=True, write_empty_values=True)
config.reload()

