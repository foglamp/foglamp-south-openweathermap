# foglamp-south-openweathermap
South Plugin for openweathermap [read more]( <https://github.com/foglamp/foglamp-south-openweathermap/blob/master/python/foglamp/plugins/south/openweathermap/readme.rst>)


### Packaging for openweathermap
This repo contains the scripts used to create a foglamp-south-openweathermap package.

#### The make_deb script
```
$ ./make_deb help

 make_deb help {x86|arm} [clean|cleanall]
This script is used to create the Debian package of foglamp south openweathermap
Arguments:
 help     - Display this help text
 x86      - Build an x86_64 package
 arm      - Build an armhf package
 clean    - Remove all the old versions saved in format .XXXX
 cleanall - Remove all the versions, including the last one
$
```

#### Building a Package

Select the architecture to use, *x86* or *arm*.
Finally, run the ``make_deb`` command:

```
$ ./make_deb arm
The package root directory is               : /home/foglamp/Development/foglamp-south-openweathermap
The FogLAMP south openweathermap version is : 1.0.0
The package will be built in                : /home/foglamp/Development/foglamp-south-openweathermap/packages/Debian/build
The architecture is set as                  : armhf
The package name is                         : foglamp-south-openweathermap-1.0.0-armhf

Populating the package and updating version file...Done.
Building the new package...
dpkg-deb: building package 'foglamp-south-openweathermap' in 'foglamp-south-openweathermap-1.0.0-armhf.deb'.
Building Complete.
$
```

The result will be:

```
$ ls -l packages/Debian/build/
total 12
drwxrwxr-x 4 foglamp foglamp 4096 Jun 20 15:19 foglamp-south-openweathermap-1.0.0-armhf
-rw-r--r-- 1 foglamp foglamp 5570 Jun 20 15:19 foglamp-south-openweathermap-1.0.0-armhf.deb
$
```

If you execute the ``make_deb`` command again, you will see:

```
$ ./make_deb arm
The package root directory is               : /home/foglamp/Development/foglamp-south-openweathermap
The FogLAMP south openweathermap version is : 1.0.0
The package will be built in                : /home/foglamp/Development/foglamp-south-openweathermap/packages/Debian/build
The architecture is set as                  : armhf
The package name is                         : foglamp-south-openweathermap-1.0.0-armhf

Saving the old working environment as foglamp-south-openweathermap-1.0.0-armhf.0001
Populating the package and updating version file...Done.
Saving the old package as foglamp-south-openweathermap-1.0.0-armhf.deb.0001
Building the new package...
dpkg-deb: building package 'foglamp-south-openweathermap' in 'foglamp-south-openweathermap-1.0.0-armhf.deb'.
Building Complete.
$
```

```
$ ls -l packages/Debian/build/
total 24
drwxrwxr-x 4 foglamp foglamp 4096 Jun 20 15:21 foglamp-south-openweathermap-1.0.0-armhf
drwxrwxr-x 4 foglamp foglamp 4096 Jun 20 15:19 foglamp-south-openweathermap-1.0.0-armhf.0001
-rw-r--r-- 1 foglamp foglamp 5570 Jun 20 15:21 foglamp-south-openweathermap-1.0.0-armhf.deb
-rw-r--r-- 1 foglamp foglamp 5570 Jun 20 15:19 foglamp-south-openweathermap-1.0.0-armhf.deb.0001
$
```
... where the previous build is now marked with the suffix *.0001*.


#### Cleaning the Package Folder

Use the ``clean`` option to remove all the old packages and the files used to make the package.
Use the ``cleanall`` option to remove all the packages and the files used to make the package.