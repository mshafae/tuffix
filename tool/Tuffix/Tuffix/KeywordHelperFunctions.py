################################################################################
# changing the system during keyword add/remove
# AUTHOR: Kevin Wortman, Jared Dyreson
################################################################################

try:
    import apt
except ImportError:
    print("[INFO] Development environment, these functions in KeywordHelperFunctions will not be available for importing")
    quit()

def add_deb_packages(package_names):
    if not (isinstance(package_names, list) and
            all(isinstance(name, str) for name in package_names)):
        raise ValueError
    print(f'[INFO] Adding all packages to the APT queue ({len(package_names)})')
    cache = apt.cache.Cache()
    cache.update()
    cache.open()
    for name in package_names:
        print(f'[INFO] Adding {name}')
        try:
            cache[name].mark_install()
        except KeyError:
            raise EnvironmentError(f'[ERROR] Deb package "{name}" not found, is this Ubuntu?')
    try:
        cache.commit()
    except Exception as e:
        raise EnvironmentError(f'[ERROR] Could not install {name}: {e}.')


def remove_deb_packages(package_names):
    if not (isinstance(package_names, list) and
            all(isinstance(name, str) for name in package_names)):
        raise ValueError
    cache = apt.cache.Cache()
    cache.update()
    cache.open()
    for name in package_names:
        try:
            cache[name].mark_delete()
        except KeyError:
            raise EnvironmentError('deb package "' + name + '" not found, is this Ubuntu?')
    try:
        cache.commit()
    except Exception as e:
        raise EnvironmentError('error removing package "' + name + '": ' + str(e))


container = ["Hello", "World", "Outo"]

class Element:
    def __init__(self):
        self.name = "Name"
    def my_name(self):
        print(self.name)
    def function_(self):
        return f'function_ {self.name}'

# TODO : TESTING 
def edit_deb_packages(package_names, is_installing):
    if not (isinstance(package_names, list) and
            all(isinstance(name, str) for name in package_names) and
            isinstance(is_installing, bool)):
        raise ValueError
    print(f'[INFO] Adding all packages to the APT queue ({len(package_names)})')
    cache = apt.cache.Cache()
    cache.update()
    cache.open()
    for name in package_names:
        print(f'[INFO] {"Installing" if is_installing else "Removing"} package: {name}')
        try:
            cache[name].mark_install() if(is_installing) else cache[name].mark_delete()
        except KeyError:
            raise EnvironmentError(f'[ERROR] Deb package "{name}" not found, is this Ubuntu?')
    try:
        cache.commit()
    except Exception as e:
        raise EnvironmentError(f'[ERROR] Could not install {name}: {e}.')


# TODO: actual implementation

# INSTALL:
# edit_packages(container, apt.apt_pkg.mark_install)

# DELETE:
# edit_packages(container, apt.apt_pkg.mark_delete)

