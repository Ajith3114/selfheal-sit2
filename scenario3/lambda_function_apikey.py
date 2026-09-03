"""
Scenario 3 - the resume reader, CONCEPT VERSION.

This one talks to the Claude API directly with an API key, instead of going
through Bedrock. Use it to teach the idea now; switch to Bedrock later when
the client's account is activated.

The only thing that changes between the two versions is WHO you ask.
Everything else - S3 wakes the Lambda, the Lambda reads the PDF, one row goes
into DynamoDB - stays exactly the same.

    this file        Lambda -> api.anthropic.com   (needs an API key)
    lambda_function  Lambda -> Bedrock             (needs no key, uses IAM)

SET THESE TWO ENVIRONMENT VARIABLES ON THE LAMBDA:
    ANTHROPIC_API_KEY = sk-ant-...
    TABLE_NAME        = resume-results
"""

import base64
import json
import os

import anthropic
import boto3

MODEL = "claude-opus-5"
TABLE = os.environ["TABLE_NAME"]

# Anthropic() picks up ANTHROPIC_API_KEY from the environment on its own,
# so the key never appears in this file.
claude = anthropic.Anthropic()

s3    = boto3.client("s3")
table = boto3.resource("dynamodb").Table(TABLE)

QUESTION = """You are screening a resume for a junior AWS / DevOps role.
Judge it and fill in the fields you are given."""

# Describing the answer as a schema means the model CANNOT reply with prose,
# or with a stray sentence before the JSON. We get valid JSON every time.
#
# Note "score" is declared as an integer. That is not decoration - DynamoDB
# rejects Python floats, so a score of 8.5 would blow up the write. Saying
# "integer" here stops that at the source.
ANSWER_SHAPE = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "name":           {"type": "string"},
            "skills_found":   {"type": "array", "items": {"type": "string"}},
            "skills_missing": {"type": "array", "items": {"type": "string"}},
            "score":          {"type": "integer"},
            "one_line":       {"type": "string"},
        },
        "required": ["name", "skills_found", "skills_missing", "score", "one_line"],
        "additionalProperties": False,
    },
}


def lambda_handler(event, context):
    # --- which file was uploaded? S3 puts it in the event ---
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key    = record["s3"]["object"]["key"]
    print(f"reading s3://{bucket}/{key}")

    # --- read the PDF and turn the bytes into text-safe base64 ---
    pdf_bytes = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    pdf_b64   = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    # --- ask Claude ---
    # The document block goes BEFORE the text block. No PDF library needed:
    # Claude reads the PDF itself.
    response = claude.messages.create(
        model=MODEL,
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64,
                    },
                },
                {"type": "text", "text": QUESTION},
            ],
        }],
        output_config={
            "effort": "low",      # a simple extraction job - cheaper and quicker
            "format": ANSWER_SHAPE,
        },
    )

    # The schema guarantees this is valid JSON, so no fence-stripping needed.
    answer = next(b.text for b in response.content if b.type == "text")
    result = json.loads(answer)
    print("claude said:", result)

    # --- one resume in, one row out ---
    table.put_item(Item={
        "resume":         key,
        "name":           result["name"],
        "score":          result["score"],
        "skills_found":   result["skills_found"],
        "skills_missing": result["skills_missing"],
        "one_line":       result["one_line"],
        "tokens_used":    response.usage.input_tokens + response.usage.output_tokens,
    })

    print(f"saved row for {key}")
    return {"ok": True, "resume": key, "score": result["score"]}
