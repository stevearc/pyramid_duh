Settings
========
``pyramid.settings`` has all the useful method for converting to non-string
data structures. It has ``asbool``, ``aslist``, ...actually that's it. We're
missing one.

.. code-block:: ini

    users =
        dsa = conspiracytheory
        president_skroob = 12345


.. code-block:: python

    def includeme(config):
        settings = config.get_settings()
        users = asdict(settings['users'])

Short and sweet.
