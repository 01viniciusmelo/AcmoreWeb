import os
import oss2
import uuid
import shortuuid
import urllib2
from mimetypes import guess_extension


class OssSaver:
    def __init__(self):
        self.access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'U6GLwyx2g6jrOL1V')
        self.access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'W05IEVd3nio2BVCG5GoMG6QekiO1di')
        self.bucket_name = os.getenv('OSS_TEST_BUCKET', 'acmore-cc')
        self.endpoint = os.getenv('OSS_TEST_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com')

        self.bucket = oss2.Bucket(oss2.Auth(self.access_key_id, self.access_key_secret), self.endpoint, self.bucket_name)

        self.static_url = 'https://static.acmore.cc/'
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        }

    def upload_file_from_url(self, file_url, diy_prefix=''):

        file_name = shortuuid.encode(uuid.uuid1())
        request = urllib2.Request(file_url, headers=self.headers)
        response = urllib2.urlopen(request)

        content_type = response.headers['Content-Type'].split()[0].rstrip(";")
        content_type_to_ext_map = {
            'image/gif':'.gif',
            'image/jpeg':'.jpg',
            'image/png':'.png',
            'image/bmp':'.bmp'
        }

        if content_type in content_type_to_ext_map:
            extension_name = content_type_to_ext_map[content_type]
        else:
            extension_name = guess_extension(content_type)

        if extension_name is None:
            extension_name = ''

        headers = {'Content-Type': '%s;' % response.headers['Content-Type']}

        self.bucket.put_object(diy_prefix+file_name+extension_name, response, headers=headers)

        cloud_file_url = self.static_url + diy_prefix + file_name + extension_name
        print 'success: %s' % cloud_file_url

        return cloud_file_url

