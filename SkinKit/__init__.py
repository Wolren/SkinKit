def classFactory(iface):
    from .skin_kit import SkinKit

    return SkinKit(iface)


def metadata():
    """Return plugin metadata dictionary.

    This is used by QGIS plugin manager and CI validation.
    """
    return {
        "name": "SkinKit",
        "version": "1.0.1",
    }


name = "SkinKit"
