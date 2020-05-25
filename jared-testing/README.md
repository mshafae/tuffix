# Footnotes

Instead of documenting all the ideas I want to implement directly into the script, this is where I will offload my thoughts.

- We are setting the `compat` flag to 19 since we want to coerce the students to be using a major release greater than or equal to 19
  - please refer to ../tuffixize.sh:40 for details to this addition
- The only foreseeable future is that `/opt/csufcs/bin` is not in the `$PATH`, so we would need to add that in the post install script
  - Users would need a default shell, and I elect bash because it is the default in Ubuntu. (This will edit `~/.bashrc`)
- Permissions for the binaries/scripts should be 755, if we want we can change that
- Makefile now should support the creation of Debian packages, the only issue is that the Make recipe needs to depend on the contents of the `tuffix` installer.
  - The current implementation just brings a list of all files in the installer directory and ignoring the DEBIAN directory
  - Make does not seem to respect it and is continues to run the recipe after 
# Dependencies

~~- `dpkg-dev`:  getting the current build architecture~~

**no longer needed, just use uname**


# External Links

- [Compat Flag](https://www.debian.org/doc/manuals/maint-guide/dother.en.html#compat)
- [How to build a simple Debian installer](https://askubuntu.com/questions/1130558/how-to-build-deb-package-for-ubuntu-18-04)

