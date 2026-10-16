"""Internal helper for the ``gen_ai_hub`` compatibility shim.

This package contains no logic of its own. Each legacy ``gen_ai_hub.*`` module is a
thin forwarder to the corresponding new ``sap_ai_sdk_*`` module. ``alias`` performs the
forwarding by replacing the shim module in ``sys.modules`` with the real target module,
which preserves object identity (so ``isinstance`` / pydantic model reuse keep working)
and makes submodule imports (e.g. ``gen_ai_hub.prompt_registry.client``) resolve against
the real package transparently.
"""

import importlib
import sys


def alias(shim_name: str, target_name: str) -> None:
    """Point the shim module ``shim_name`` at the real module ``target_name``.

    Call from a shim ``__init__.py`` as ``alias(__name__, "sap_ai_sdk_...")``. After this
    runs, ``sys.modules[shim_name]`` *is* the target module object.
    """
    sys.modules[shim_name] = importlib.import_module(target_name)
