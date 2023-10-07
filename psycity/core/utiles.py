import os
import hashlib
from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        file_name = hashlib.sha1(instance.body.read()).hexdigest()
        # set filename as random string
        filename_with_ext = '{}.{}'.format(file_name, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename_with_ext)
