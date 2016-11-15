# Frontend commit

Take everything and put it into a S3 bucket which will then be served through Cloudfront.

To use:
```
export AWS_ACCESS_KEY_ID='Your AWS access key id goes here'
export AWS_SECRET_ACCESS_KEY='Your AWS secret access key goes here'
python s3commit.py <static-folder> <s3-bucket> <project-name>

```

Marketing example:
```
export AWS_ACCESS_KEY_ID='Your AWS access key id goes here'
export AWS_SECRET_ACCESS_KEY='Your AWS secret access key goes here'
cd ~/frontend-commit
python s3commit.py ../marketing-website/static hello-cdn marketing
```
