# -*- coding: utf-8 -*-
def classFactory(iface):
    from .skin_kit import SkinKit

    return SkinKit(iface)
