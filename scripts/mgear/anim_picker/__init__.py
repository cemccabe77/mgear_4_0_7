from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from . import gui
from . import version

__version__ = version.__version__


# =============================================================================
# Load user interface function
# =============================================================================
def load(edit=False, dockable=False, *args, **kwargs):
    """To launch the ui and not get the same instance

    Returns:
        Anim_picker: instance

    Args:
        edit (bool, optional): Description
        dockable (bool, optional): Description

    """
    return gui.load(edit=edit, dockable=dockable)
