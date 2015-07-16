# frontend-commit

Take everything and put it into a S3 bucket which will then be served through Cloudfront.

To use:
```
EXPORT AWS_ACCESS_KEY_ID = 'Your AWS access key id goes here'
EXPORT AWS_SECRET_ACCESS_KEY = 'Your AWS secret access key goes here'
python s3deploy.py <static-folder> <s3-bucket> <project-name>

For example:
```
python s3deploy.py ./marketing-website/static hello-cdn marketing
python s3deploy.py ./preorders/static hello-cdn store

```
