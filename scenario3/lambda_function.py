"""
Scenario 3 - the resume reader.

What this does, in the same order as the video:
    1. Somebody uploads resume.pdf to S3
    2. S3 wakes this Lambda up and tells it the file name
    3. Lambda reads the PDF from S3
    4. Lambda asks Bedrock to judge it
    5. Lambda writes one row into DynamoDB
    6. Lambda goes back to sleep
"""

import json
import os
import boto3

# The model id MUST have the "global." prefix.
#
# If you use the plain id "anthropic.claude-opus-5" you get this error:
#   ValidationException: Invocation of model ID anthropic.claude-opus-5 with
#   on-demand throughput isn't supported. Retry your request with the ID or
#   ARN of an inference profile that contains this model.
#
# It looks like a permissions problem, but it is not. The newer Claude models
# are only callable through an "inference profile", and "global." is the name
# of that profile.
MODEL = "global.anthropic.claude-opus-5"

TABLE = os.environ["TABLE_NAME"]

s3      = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")
table   = boto3.resource("dynamodb").Table(TABLE)

# We ask for JSON so the answer is easy to store.
# "score" is a whole number on purpose - DynamoDB does not like Python floats.
QUESTION = """You are screening a resume for a junior AWS / DevOps role.

Reply with ONLY this JSON, nothing else:
{
  "name": "the candidate's name, or unknown",
  "skills_found": ["skills they clearly have"],
  "skills_missing": ["important skills for the role that are absent"],
  "score": 0,
  "one_line": "one sentence a recruiter can read"
}

"score" must be a whole number from 0 to 100."""


def lambda_handler(event, context):
    # --- 2. which file was uploaded? S3 puts it in the event ---
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key    = record["s3"]["object"]["key"]
    print(f"reading s3://{bucket}/{key}")

    # --- 3. read the PDF ---
    pdf_bytes = s3.get_object(Bucket=bucket, Key=key)["Body"].read()

    # --- 4. ask Bedrock ---
    # We hand Bedrock the PDF itself. No PDF library needed - Bedrock reads it.
    reply = bedrock.converse(
        modelId=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"document": {
                    "format": "pdf",
                    "name": "resume",            # letters only, no dots or dashes
                    "source": {"bytes": pdf_bytes},
                }},
                {"text": QUESTION},
            ],
        }],
        inferenceConfig={"maxTokens": 1000},
    )

    answer = reply["output"]["message"]["content"][0]["text"].strip()

    # The model sometimes wraps JSON in ```json fences. Take them off.
    if answer.startswith("```"):
        answer = answer.split("```")[1].removeprefix("json").strip()

    result = json.loads(answer)
    print("bedrock said:", result)

    # --- 5. one resume in, one row out ---
    table.put_item(Item={
        "resume":         key,                                # which file
        "name":           result.get("name", "unknown"),
        "score":          int(result.get("score", 0)),
        "skills_found":   result.get("skills_found", []),
        "skills_missing": result.get("skills_missing", []),
        "one_line":       result.get("one_line", ""),
        "tokens_used":    reply["usage"]["totalTokens"],
    })

    print(f"saved row for {key}")
    return {"ok": True, "resume": key, "score": result.get("score")}
