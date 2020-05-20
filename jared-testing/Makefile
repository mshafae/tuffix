SHELL=bash
PKG_BASE=tuffix-installer
PKG_DIR_OUTPUT=builds

PKG_NAME=tuffix
PKG_REVISION=1
PKG_VERSION=0
PKG_ARCH := $(shell uname -m)
PKG_OUT=$(PKG_NAME)_$(PKG_REVISION)-$(PKG_VERSION)_$(PKG_ARCH).deb

#vpath % $(PKG_BASE)

deb: $(OBJS)
	#./update_information $(PKG_BASE)
	#dpkg-deb --build $(PKG_BASE) $(OUTPUT)/$(PKG_OUT)
