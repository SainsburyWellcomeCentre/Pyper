import os
from configobj import ConfigObj


config_path = os.path.expanduser(os.path.normcase('~/.motion_tracking.conf'))
config = ConfigObj(config_path, encoding="UTF8", indent_type='    ', unrepr=True,
                   create_empty=True, write_empty_values=True)
config.reload()

