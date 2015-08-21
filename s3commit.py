#! /usr/bin/env python
import os, sys, boto, mimetypes, zipfile, gzip
from io import StringIO, BytesIO
from optparse import OptionParser
from jsmin import *
from cssmin import *
from datetime import datetime, timedelta
import hashlib

# The list of content types to gzip, add more if needed
COMPRESSIBLE = [
    'text/plain',
    'text/csv',
    'application/xml',
    'application/javascript',
    'text/css'
]
CDN_ROOT = '//hellocdn.net/'
STATIC_NAME = 'static'

def main():
    parser = OptionParser(usage='usage: %prog [options] src_folder destination_bucket_name prefix')

    (options, args) = parser.parse_args()
    if len(args) != 3:
        parser.error("incorrect number of arguments")
    src_folder = os.path.normpath(args[0])
    bucket_name = args[1]
    prefix = args[2]

    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket_name)

    DEPLOY_VERSION_FILE = src_folder + '/s3deploy.txt'
    S3_VERSION_FILE = prefix + '.s3deploy.txt'

    if bucket.get_key(S3_VERSION_FILE):
        print 'Deploy version exists'
        key = bucket.new_key(S3_VERSION_FILE)
        previous_version = int(key.get_contents_as_string())
        version = previous_version + 1

        file = open(DEPLOY_VERSION_FILE, 'w')
        file.write(str(version))
        file.close()
    else:
        print 'Deploy version doesn\'t exist'
        file = open(DEPLOY_VERSION_FILE, 'r')
        version = file.read()

    key = bucket.new_key(S3_VERSION_FILE)
    headers = {'Content-Type': 'text/plain', 'x-amz-acl': 'public-read'}
    content = open(DEPLOY_VERSION_FILE)
    key.set_contents_from_file(content, headers)

    namelist = []

    for root, dirs, files in os.walk(src_folder):
        if files and not '.webassets' in root:
            path = os.path.relpath(root, src_folder)
            namelist += [os.path.normpath(os.path.join(path, f)) for f in files]

    print 'Uploading %d files to bucket %s' % (len(namelist), bucket.name)

    replace = {}

    for name in namelist:
        type, encoding = mimetypes.guess_type(name)
        type = type or 'application/octet-stream'

        if 'image' in type:
            root = '/' + STATIC_NAME + '/' + name
            key = prefix + str(version) + name
            key = hashlib.md5(key).hexdigest() + '.' + name.split('.')[-1]

            replace[root] = key

    keys = {
        'old': [],
        'new': []
    }

    for name in namelist:
        if '.DS_Store' not in name and '.scss' not in name:
            key = hashlib.md5(prefix + str(version) + name).hexdigest() + '.' + name.split('.')[-1]
            old_key = hashlib.md5(prefix + str((int(version) - 1)) + name).hexdigest() + '.' + name.split('.')[-1]

            keys['old'].append(old_key)
            keys['new'].append(key)

            content = open(os.path.join(src_folder, name))

            expires = datetime.utcnow() + timedelta(days=(25 * 365))
            expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

            type, encoding = mimetypes.guess_type(name)
            type = type or 'application/octet-stream'
            headers = {
                'Content-Type': type,
                'Expires': expires,
                'x-amz-acl': 'public-read',
                'Cache-Control': 'public'
            }
            states = [type]

            # Also upload retina version
            if 'image' in type and '@' in name and 'x.' in name:
                retina = name.split('@')[1].split('x')[0]
                key = hashlib.md5(prefix + str(version) + name).hexdigest() + '@' + retina + 'x.' + name.split('.')[-1]

            key = bucket.new_key(key)

            if type == 'application/javascript':
                outs = StringIO()
                JavascriptMinify().minify(content, outs)
                content.close()
                content = outs.getvalue()
                if len(content) > 0 and content[0] == '\n':
                    content = content[1:]
                content = BytesIO(content)
                states.append('minified')

            if type == 'text/css':
                outs = cssmin(content.read())

                for k, v in replace.iteritems():
                    v = CDN_ROOT + v
                    outs = outs.replace(k, v)

                content.close()
                content = outs

                if len(content) > 0 and content[0] == '\n':
                    content = content[1:]

                content = BytesIO(content)
                states.append('minified')

            if type in COMPRESSIBLE:
                headers['Content-Encoding'] = 'gzip'
                compressed = StringIO()
                gz = gzip.GzipFile(filename=name, fileobj=compressed, mode='w')
                gz.writelines(content)
                gz.close()
                content.close
                content = BytesIO(compressed.getvalue())
                states.append('gzipped')

            states = ', ' . join(states)
            print '- %s => %s (%s)' % (name, key.name, states)
            key.set_contents_from_file(content, headers)
            content.close()

    # Delete old versions
    #bucket.delete_keys(keys['old'])

if __name__ == '__main__':
    main()
