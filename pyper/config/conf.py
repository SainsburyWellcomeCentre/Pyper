import os
from configobj import ConfigObj


config_path = os.path.expanduser(os.path.normcase('~/.pyper.conf'))
if not os.path.exists(config_path):
    config_path = 'config/pyper.conf'  # FIXME: relies on working directory
config = ConfigObj(config_path, encoding="UTF8", indent_type='    ', unrepr=True,
                   create_empty=True, write_empty_values=True)
config.reload()

