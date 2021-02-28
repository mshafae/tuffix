##########################################################################
# changing the system during keyword add/remove
# AUTHOR: Kevin Wortman, Jared Dyreson
##########################################################################

import apt


def edit_deb_packages(package_names, is_installing):
    if not (isinstance(package_names, list) and
            all(isinstance(name, str) for name in package_names) and
            isinstance(is_installing, bool)):
        raise ValueError
    print(
        f'[INFO] Adding all packages to the APT queue ({len(package_names)})')
    cache = apt.cache.Cache()
    cache.update()
    cache.open()
    for name in package_names:
        print(
            f'[INFO] {"Installing" if is_installing else "Removing"} package: {name}')
        try:
            cache[name].mark_install() if(
                is_installing) else cache[name].mark_delete()
        except KeyError:
            raise EnvironmentError(
                f'[ERROR] Deb package "{name}" not found, is this Ubuntu?')
    try:
        cache.commit()
    except Exception as e:
        raise EnvironmentError(f'[ERROR] Could not install {name}: {e}.')
