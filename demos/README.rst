===============
aioTelebot demo
===============

aioTelebot demo is a simple script create to check aioTelebot feature. It cannot be used as a regular bot.
It is powered by click python library.


In order to use this demo you must call script setting auth token provided by @botfather.

.. code-block:: bash

    $ python demo.py --token <yourBotToken> <action> <action parameters>

All request and responses will be written on ``logs/service.log`` allowing you to trace your requests.

------
get_me
------

This script returns information about your bot.

Syntax
======

.. code-block:: bash

    $ python demo.py --token <yourBotToken> get_me


Example
=======

.. code-block:: bash

    $ python demo.py --token aaaabbbb:eweweewewewweweew get_me

-----------
get_updates
-----------

This script returns pendant updates.


Syntax
======

.. code-block:: bash

    $ python demo.py --token <yourBotToken> get_updates


Example
=======

.. code-block:: bash

    $ python demo.py --token aaaabbbb:eweweewewewweweew get_updates

It is possible to set offset using parameter ``--offset`` or ``-o`` in order to avoid
to get old updates. In the same way it is possible to set ``--timeout`` or ``-t`` parameter
in order to define how much time request must be paused before return with no results.

--------
get_file
--------

This script allow you to request a file path to some file using its id.


Syntax
======

.. code-block:: bash

    $ python demo.py --token <yourBotToken> get_file <fileId>


Example
=======

.. code-block:: bash

    $ python demo.py --token aaaabbbb:eweweewewewweweew get_file 34433423

-------------
download_file
-------------

This script allows you to download a file using a file path. All files are stored on download directory.


Syntax
======

.. code-block:: bash

    $ python demo.py --token <yourBotToken> download_file <filePath>


Example
=======

.. code-block:: bash

    $ python demo.py --token aaaabbbb:eweweewewewweweew download_file files/file1.jpg


-----------------------
get_user_profile_photos
-----------------------

This script allows you get user profile pictures. Use ``--offset`` or ``-o`` parameter
to avoid firsts items. And use ``--limit`` or ``-l`` parameter to limit list length.

Syntax
======

.. code-block:: bash

    $ python demo.py --token <yourBotToken> get_user_profile_photos <userId> [--offset <offset>] [--limit <limit>]


Example
=======

.. code-block:: bash

    $ python demo.py --token aaaabbbb:eweweewewewweweew get_user_profile_photos 1000001

------------
send_message
------------

This script allows to send message to a chat. It is possible to define a replay markup.
Use parameter ``--reply-markup`` or ``-m`` to define markup type. Available types are
``inline`` and ``reply``. And use ``--reply`` or ``-r`` to define each button.



Syntax
======

.. code-block:: bash

    $ python demo.py --token <yourBotToken> send_message <text> [--reply-markup <markupType> [--reply <buttonText>]]


Example
=======

.. code-block:: bash

    $ python demo.py --token aaaabbbb:eweweewewewweweew send_message test --reply-markup inline \
    --reply button1 --reply button2 --reply button3

----------
send_photo
----------

This script allows to send picture to a chat. It is possible to define a replay markup.
Use parameter ``--reply-markup`` or ``-m`` to define markup type. Available types are
``inline`` and ``reply``. And use ``--reply`` or ``-r`` to define each button.



Syntax
======

.. code-block:: bash

    $ python demo.py --token <yourBotToken> send_photo <pathToFile> [--reply-markup <markupType> [--reply <buttonText>]]


Example
=======

.. code-block:: bash

    $ python demo.py --token aaaabbbb:eweweewewewweweew send_photo ../data/picture.jpg --reply-markup inline \
    --reply button1 --reply button2 --reply button3