#!/usr/bin/env bash
# Scenario 3 - build the whole thing from nothing.
# Run it once:  bash scenario3/deploy.sh
set -e

# ---------- names you can change ----------
REGION=ap-south-1
ACCOUNT=753804209871
BUCKET=6f-resumes-demo                 # where resumes get uploaded
TABLE=resume-results                   # where the answers go
FUNC=resume-reader                     # the Lambda
ROLE=resume-reader-role
MODEL=global.anthropic.claude-opus-5   # note the "global." prefix

echo "== 1. DynamoDB table (holds the answer) =="
aws dynamodb create-table \
  --table-name "$TABLE" \
  --attribute-definitions AttributeName=resume,AttributeType=S \
  --key-schema AttributeName=resume,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region "$REGION" >/dev/null || echo "  (table already exists)"

aws dynamodb wait table-exists --table-name "$TABLE" --region "$REGION"
echo "  table ready"

echo "== 2. S3 bucket (holds the file) =="
aws s3 mb "s3://$BUCKET" --region "$REGION" || echo "  (bucket already exists)"

echo "== 3. IAM role for the Lambda =="
# Who is allowed to wear this role: Lambda.
aws iam create-role --role-name "$ROLE" \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow",
                  "Principal":{"Service":"lambda.amazonaws.com"},
                  "Action":"sts:AssumeRole"}]}' >/dev/null || echo "  (role already exists)"

# Lets the Lambda write logs.
aws iam attach-role-policy --role-name "$ROLE" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# What the Lambda is allowed to touch: this bucket, this table, this model.
#
# NOTE the three Bedrock ARNs. The "global." profile forwards your call to the
# real model, so you must allow the profile AND the model it forwards to.
# Allowing only the profile gives AccessDeniedException, which looks like the
# model is not enabled - it is.
aws iam put-role-policy --role-name "$ROLE" --policy-name resume-reader-access \
  --policy-document "{
    \"Version\":\"2012-10-17\",
    \"Statement\":[
      {\"Effect\":\"Allow\",\"Action\":\"s3:GetObject\",
       \"Resource\":\"arn:aws:s3:::$BUCKET/*\"},
      {\"Effect\":\"Allow\",\"Action\":\"dynamodb:PutItem\",
       \"Resource\":\"arn:aws:dynamodb:$REGION:$ACCOUNT:table/$TABLE\"},
      {\"Effect\":\"Allow\",\"Action\":\"bedrock:InvokeModel\",\"Resource\":[
         \"arn:aws:bedrock:$REGION:$ACCOUNT:inference-profile/$MODEL\",
         \"arn:aws:bedrock:::foundation-model/anthropic.claude-opus-5\",
         \"arn:aws:bedrock:$REGION::foundation-model/anthropic.claude-opus-5\"]}
    ]}"

echo "  waiting 10s for the role to spread across AWS"
sleep 10

echo "== 4. the Lambda itself =="
cd scenario3
zip -q -j /tmp/resume-reader.zip lambda_function.py
cd ..

aws lambda create-function \
  --function-name "$FUNC" \
  --runtime python3.12 \
  --handler lambda_function.lambda_handler \
  --role "arn:aws:iam::$ACCOUNT:role/$ROLE" \
  --zip-file fileb:///tmp/resume-reader.zip \
  --timeout 120 \
  --memory-size 512 \
  --environment "Variables={TABLE_NAME=$TABLE}" \
  --region "$REGION" >/dev/null \
|| aws lambda update-function-code \
     --function-name "$FUNC" \
     --zip-file fileb:///tmp/resume-reader.zip \
     --region "$REGION" >/dev/null

aws lambda wait function-active-v2 --function-name "$FUNC" --region "$REGION"
echo "  lambda ready"

echo "== 5. make the upload wake the Lambda =="
# Step 1: allow S3 to call the Lambda.
aws lambda add-permission \
  --function-name "$FUNC" \
  --statement-id s3-can-call-me \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn "arn:aws:s3:::$BUCKET" \
  --region "$REGION" >/dev/null || echo "  (permission already there)"

# Step 2: tell the bucket to call it on every new .pdf.
aws s3api put-bucket-notification-configuration --bucket "$BUCKET" \
  --notification-configuration "{
    \"LambdaFunctionConfigurations\":[{
      \"LambdaFunctionArn\":\"arn:aws:lambda:$REGION:$ACCOUNT:function:$FUNC\",
      \"Events\":[\"s3:ObjectCreated:*\"],
      \"Filter\":{\"Key\":{\"FilterRules\":[{\"Name\":\"suffix\",\"Value\":\".pdf\"}]}}
    }]}"

echo
echo "Done. Now try it:"
echo "  aws s3 cp resume.pdf s3://$BUCKET/"
echo "  aws dynamodb scan --table-name $TABLE --region $REGION"
