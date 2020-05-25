SHELL=bash
PKG_BASE=tuffix-installer
PKG_DIR_OUTPUT=builds

PKG_NAME=tuffix
PKG_ARCH := $(shell uname -m)

objects = hello.o goodbye.o main.o

TARGET = main

all: $(objects) update_information
	$(CC) -o $(TARGET) $(objects)
	$(eval PKG_REVISION := $$(shell awk '/Version:/ {print $$2}' $(PKG_BASE)/DEBIAN/control | cut -d "-" -f1))
	$(eval PKG_VERSION := $$(shell awk '/Version:/ {print $$2}' $(PKG_BASE)/DEBIAN/control | cut -d "-" -f2))
	$(eval PKG_UPDATED=$(shell echo $$(($(PKG_VERSION)+1))))
	find $(PKG_BASE) -type f -not -path "*DEBIAN*" -exec chmod 755 {} \;
	sed -i "s/Version: .*/Version: $(PKG_REVISION)-$(PKG_UPDATED)/" $(PKG_BASE)/DEBIAN/control
	dpkg-deb --build $(PKG_BASE) $(PKG_DIR_OUTPUT)/$(PKG_NAME)_$(PKG_REVISION)_$(PKG_UPDATED)_$(PKG_ARCH).deb

main.o: $(PKG_BASE)/opt/csufcs/bin/main.c
	$(CC) -c $< 
hello.o: $(PKG_BASE)/opt/csufcs/bin/hello.c
	$(CC) -c $<
goodbye.o: $(PKG_BASE)/opt/csufcs/bin/goodbye.c
	$(CC) -c $<
clean:
	rm $(objects)
spotless: clean
	rm $(TARGET)
