""" pyramid_duh """
from .params import argify
from .route import ISmartLookupResource, IStaticResource, IModelResource
from .view import addslash

__version__ = '0.1.2'


def includeme(config):
    """ Add request methods """
    config.include('pyramid_duh.params')
    config.include('pyramid_duh.view')
