#!/usr/bin/env bash
# Makes the zip you upload to Lambda for the API-key version.
#
# Why a zip at all?
#   boto3 is already inside Lambda, so the Bedrock version can be pasted
#   straight into the console editor. The "anthropic" package is NOT inside
#   Lambda, so it has to travel with your code.
#
# Run:  bash scenario3/build-apikey-zip.sh
set -e

cd "$(dirname "$0")"
rm -rf build resume-reader-apikey.zip

echo "1. downloading the anthropic package"
pip install anthropic -t build/ --quiet

echo "2. adding our code (Lambda looks for lambda_function.py)"
cp lambda_function_apikey.py build/lambda_function.py

echo "3. zipping"
cd build
zip -qr ../resume-reader-apikey.zip .
cd ..
rm -rf build

echo
echo "Done: scenario3/resume-reader-apikey.zip ($(du -h resume-reader-apikey.zip | cut -f1))"
echo
echo "Now in the console:"
echo "  Lambda -> resume-reader -> Code -> Upload from -> .zip file"
echo
echo "And set these two environment variables:"
echo "  ANTHROPIC_API_KEY = sk-ant-..."
echo "  TABLE_NAME        = resume-results"
