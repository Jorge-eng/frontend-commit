# Frontend commit

Take everything and put it into a S3 bucket which will then be served through Cloudfront.

To use:
```
EXPORT AWS_ACCESS_KEY_ID = 'Your AWS access key id goes here'
EXPORT AWS_SECRET_ACCESS_KEY = 'Your AWS secret access key goes here'
python s3commit.py <static-folder> <s3-bucket> <project-name>
```
