""" pyramid_duh """
from .params import argify
from .route import ISmartLookupResource, IStaticResource, IModelResource
from .view import CustomPredicateConfig, addslash, subpath

try:
    from ._version import *  # pylint: disable=F0401,W0401
except ImportError:
    __version__ = 'unknown'


def includeme(config):
    """ Add request methods """
    config.include('pyramid_duh.params')
