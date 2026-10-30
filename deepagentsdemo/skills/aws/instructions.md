# AWS - Instructions

## Pick the right service
- Run code without servers, short tasks -> **Lambda**.
- Long-running app / full control -> **EC2** (or **ECS/Fargate** for containers).
- Store files -> **S3**. Relational DB -> **RDS**. Key-value -> **DynamoDB**.
- Use LLMs (Claude, Llama...) as a managed API -> **Bedrock**.
Explain why the chosen service fits better than the alternatives.

## Security rules (always apply)
- Never hard-code access keys; use IAM roles or `aws configure` / environment variables.
- Least privilege: give IAM policies only the actions really needed.
- S3 buckets private by default; enable encryption.

## Costs
- Mention the pricing model (per request, per hour, per GB) and the free tier if relevant.
- Warn about resources that keep costing money if not deleted (EC2, NAT Gateway, RDS).

## Answer format
- Give AWS CLI commands or boto3 code in code blocks.
- Always specify the region (e.g. `eu-west-3` = Paris).
- Cite the official AWS documentation page when possible (docs.aws.amazon.com).
