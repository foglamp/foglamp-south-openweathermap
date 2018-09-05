============================
foglamp-south-openweathermap
============================

South Plugin for openweathermap `read more <https://github.com/foglamp/foglamp-south-openweathermap/blob/master/python/foglamp/plugins/south/openweathermap/readme.rst>`_


****************************
Packaging for openweathermap
****************************

This repo contains the scripts used to create a foglamp-south-openweathermap debian package.

The make_deb script
===================

.. code-block:: console

    $ ./make_deb help

    make_deb help [clean|cleanall]
    This script is used to create the Debian package of foglamp south openweathermap
    Arguments:
    help     - Display this help text
    clean    - Remove all the old versions saved in format .XXXX
    cleanall - Remove all the versions, including the last one
    $


Building a Package
==================

Finally, run the ``make_deb`` command:

.. code-block:: console

    $ ./make_deb
    The package root directory is               : /home/foglamp/Development/foglamp-south-openweathermap
    The FogLAMP south openweathermap version is : 1.0.0
    The package will be built in                : /home/foglamp/Development/foglamp-south-openweathermap/packages/build
    The package name is                         : foglamp-south-openweathermap-1.0.0

    Populating the package and updating version file...Done.
    Building the new package...
    dpkg-deb: building package 'foglamp-south-openweathermap' in 'foglamp-south-openweathermap-1.0.0.deb'.
    Building Complete.
    $


The result will be:

.. code-block:: console

    $ ls -l packages/build/
    total 12
    drwxrwxr-x 4 foglamp foglamp 4096 Jun 20 15:19 foglamp-south-openweathermap-1.0.0
    -rw-r--r-- 1 foglamp foglamp 5570 Jun 20 15:19 foglamp-south-openweathermap-1.0.0.deb
    $


If you execute the ``make_deb`` command again, you will see:

.. code-block:: console

    $ ./make_deb
    The package root directory is               : /home/foglamp/Development/foglamp-south-openweathermap
    The FogLAMP south openweathermap version is : 1.0.0
    The package will be built in                : /home/foglamp/Development/foglamp-south-openweathermap/packages/build
    The package name is                         : foglamp-south-openweathermap-1.0.0

    Saving the old working environment as foglamp-south-openweathermap-1.0.0.0001
    Populating the package and updating version file...Done.
    Saving the old package as foglamp-south-openweathermap-1.0.0.deb.0001
    Building the new package...
    dpkg-deb: building package 'foglamp-south-openweathermap' in 'foglamp-south-openweathermap-1.0.0.deb'.
    Building Complete.
    $



    $ ls -l packages/build/
    total 24
    drwxrwxr-x 4 foglamp foglamp 4096 Jun 20 15:21 foglamp-south-openweathermap-1.0.0
    drwxrwxr-x 4 foglamp foglamp 4096 Jun 20 15:19 foglamp-south-openweathermap-1.0.0.0001
    -rw-r--r-- 1 foglamp foglamp 5570 Jun 20 15:21 foglamp-south-openweathermap-1.0.0.deb
    -rw-r--r-- 1 foglamp foglamp 5570 Jun 20 15:19 foglamp-south-openweathermap-1.0.0.deb.0001
    $


... where the previous build is now marked with the suffix *.0001*.


Cleaning the Package Folder
===========================


Use the ``clean`` option to remove all the old packages and the files used to make the package.
Use the ``cleanall`` option to remove all the packages and the files used to make the package.