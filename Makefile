# this Makefile will generate a Debian file for the Tuffix installer
# Written by Jared Dyreson and in conjunction with Michael Shafae
# California State University Fullerton

SHELL=bash
PKG_BASE=TuffixInstaller
PKG_DIR_OUTPUT=builds

PKG_NAME=tuffix
PKG_ARCH := $(shell uname -m)

all: 
	$(MAKE) update_and_build

update_and_build: $(TARGET)
	$(eval PKG_REVISION := $$(shell sed -n -e 's/^.*Version: //p' $(PKG_BASE)/DEBIAN/control| sed "s/^[ \t]*//" | cut -d "-" -f1))
	$(eval PKG_VERSION := $$(shell sed -n -e 's/^.*Version: //p' $(PKG_BASE)/DEBIAN/control| sed "s/^[ \t]*//" | cut -d "-" -f2))
	$(eval PKG_UPDATED=$(shell echo $$(($(PKG_VERSION)+1))))
	find $(PKG_BASE) -type f -not -path "*DEBIAN*" -exec chmod 755 {} \;
	sed -i "s/Version: .*/Version: $(PKG_REVISION)-$(PKG_UPDATED)/" $(PKG_BASE)/DEBIAN/control
	dpkg-deb --build $(PKG_BASE) $(PKG_DIR_OUTPUT)/$(PKG_NAME)_$(PKG_REVISION)_$(PKG_UPDATED)_$(PKG_ARCH).deb
