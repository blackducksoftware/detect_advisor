import tarfile

def is_tar_docker(the_file):
    try:
        tar = tarfile.open(the_file)
        names = tar.getnames()
        for name in names:
            parts = name.split("/")
            if len(parts) > 1:
                if parts[1] == "layer.tar":
                    tar.close()
                    return True
        tar.close()
        return False
    except:
        return False

    """
    the_file = "/Users/damonw/bds/problems/trailheads/strange_debian_postgres/strange_debian.tar"
    foo = is_tar_docker(the_file)
    print(foo)
    """
