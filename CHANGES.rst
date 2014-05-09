Changelog
=========

0.1.2
-----
* Bug fix: Fix potential timezone issue when converting unix time to datetime
* Using the 'six' library for python 2/3 compatibility

0.1.1
-----
* Bug fix: IStaticResource fails to look up self.request if nested 2-deep
* Bug fix: Name collisions with version_helper.py
* Bug fix: Subpath glob matching always respects case
* Feature: @argify works on view classes
* Feature: @argify can inject types that consume multiple parameters
* Feature: Parameter types can be a dotted path

0.1.0
-----
* Package released into the wild
