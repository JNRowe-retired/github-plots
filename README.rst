================================================================================
github-plots - Misc alternate Github plots
================================================================================

:Authors:
    Scott Torborg (scott@cartlogic.com)
:Version: 0.1

Currently supported modes:

``issues`` - builds an ascii plot of the number of issues for your repo over time.


Quick start::

    $ cat > ~/.github
    [github]
    username = joeuser
    api_token = deadbeefcafebabe...
    requests_per_second = 1
    $ pip install github-plots
    $ github-plots issues joeuser/myrepo


License
=======

This software is licensed under the ``MIT License``.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround
