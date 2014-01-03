""" pyramid_duh """
from .params import argify
from .route import ISmartLookupResource, IStaticResource, IModelResource
from .view import addslash

try:
    from ._version import *  # pylint: disable=F0401,W0401
except ImportError:  # pragma: no cover
    __version__ = 'unknown'


def includeme(config):
    """ Add request methods """
    config.include('pyramid_duh.params')
    config.include('pyramid_duh.view')
