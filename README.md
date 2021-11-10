#### Serverless Image Labelling

<img src="https://user-images.githubusercontent.com/10434677/138452508-a60f787f-5d95-4120-ad7c-c89045f06795.png" width="600" height="500" />

#### Use-Cases

Storing images in S3 Bucket with label information. **AWS Rekognition** is used for detecting labels in image. You can later query the API endpoint provided by this serverless service to get the list of images which belongs to particular label. 

On deploying, this provisions 3 Lambda functions in your AWS setup. One Lambda function is responsible to create a presigned url for image upload,the other  store the image labels on each successful PUT operation in specified S3 bucket. The final Lambda function is used to process the call back url trigger by dynamoDb stream.

#### Usage

This project uses `serverless` framework. So, make sure you get that first and give the necessary permissions to `serverless cli`. Follow [this page](https://www.serverless.com/framework/docs/getting-started/) for getting started. <br>
Before `sls deploy`, make sure you have setup these resources in AWS.
```
User Workflow

1. Send request with optionally provided callback_url in request body. Response return unique upload_url.

2. The user uploads a picture to the upload_url

3. Once the image has been PUT to the upload_url, it gets stored in an S3 bucket. Once successfully stored, this will trigger the image recognition process

4 Once the image recognition process finishes, the user receives a callback under the callback_url they indicated in the first step

5. User can also retrieve the results from a GET endpoint

```

```
# Install the necessary plugin
$ sls plugin install -n serverless-python-requirements
```
```
# Deploy to AWS
$ sls deploy
```
After deployment is successful, you can check the setup details using `sls info` . Now, you can test the services by 
creating a pre-signed url to upload images on **S3.** This would label the image and store the details in **DyanamoDB**. You can later query the endpoint for getting images associated to the label.

Also, you can provide a callback url as a POST body params when creating a pres-signed url

Example,

    curl --location --request POST 
    ' https://4p6353orce.execute-api.us-west-2.amazonaws.com/dev/blobs' \--data-raw ''
    
    curl --location -g --request GET 
    ' https://4p6353orce.execute-api.us-west-2.amazonaws.com/dev/blobs/{blob_id}'
      

