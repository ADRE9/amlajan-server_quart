ALLOWED_EXTENSIONS = set(["PNG"])


def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in ALLOWED_EXTENSIONS:
        return True
    else:
        return False
