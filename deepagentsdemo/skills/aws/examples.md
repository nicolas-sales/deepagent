# AWS - Examples

## Example 1 - Upload a file to S3 with boto3
```python
import boto3

s3 = boto3.client("s3", region_name="eu-west-3")
s3.upload_file("report.pdf", "my-private-bucket", "reports/report.pdf")
```
- Credentials come from `aws configure` or an IAM role, never from the code.
- Source: https://docs.aws.amazon.com/boto3/latest/guide/s3-uploading-files.html

## Example 2 - Call a Claude model on Bedrock
```python
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
response = bedrock.converse(
    modelId="<model-id from the Bedrock console>",
    messages=[{"role": "user", "content": [{"text": "Hello"}]}],
)
print(response["output"]["message"]["content"][0]["text"])
```
- The model must first be enabled in Bedrock > Model access.
- Cost: billed per input/output token.
