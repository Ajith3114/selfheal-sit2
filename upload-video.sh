#!/usr/bin/env bash
# ============================================================
#  6F School of IT - put the scenario videos on the live site
#
#  The deploy pipeline only ships index.html. Videos are big and
#  they almost never change, so they get their own one-off upload
#  instead of riding along on every git push.
#
#  Run it after you render, or re-render, a scene:
#      bash upload-video.sh
#
#  Needs working AWS credentials. If you see "ExpiredToken",
#  refresh them first - nothing below will work until you do.
# ============================================================
set -euo pipefail

BUCKET="vignesh-web-2k26"
DIST_ID="E1MG8RKBCM89YT"
REGION="ap-south-1"
SITE_URL="https://d38etqdlxtduo5.cloudfront.net"
SRC="${1:-./video}"          # folder holding scenarioN.mp4 and scenarioN.jpg

export AWS_DEFAULT_REGION="$REGION"

if [ ! -d "$SRC" ]; then
  echo "ERROR: no such folder: $SRC"
  echo "  render the scenes first, then re-run this."
  exit 1
fi

COUNT=$(find "$SRC" -maxdepth 1 -name '*.mp4' | wc -l | tr -d ' ')
if [ "$COUNT" = "0" ]; then
  echo "ERROR: no .mp4 files in $SRC"
  exit 1
fi
echo "==> found $COUNT video(s) in $SRC"

# S3 object keys are case-sensitive; Windows filenames are not. So a file that
# looks fine locally as Scenario1.mp4 becomes a 404 for index.html, which asks
# for video/scenario1.mp4. Compare exactly, before anything is uploaded.
INDEX="./index.html"
if [ -f "$INDEX" ]; then
  echo "==> checking filenames match what index.html asks for"
  BAD=0
  for want in $(grep -o 'video/scenario[0-9]\.\(mp4\|jpg\)' "$INDEX" \
                  | sed 's|video/||' | sort -u); do
    if ! ls -1 "$SRC" | grep -qx "$want"; then
      echo "    MISSING or WRONG CASE: $want"
      BAD=1
    fi
  done
  if [ "$BAD" != "0" ]; then
    echo "ERROR: rename the files above to match exactly, then re-run."
    echo "  (a case-only rename needs two steps: mv X X.tmp && mv X.tmp x)"
    exit 1
  fi
  echo "    all names match"
fi

# Fail early and clearly if the credentials are stale, rather than
# half-way through an upload.
echo "==> checking credentials"
aws sts get-caller-identity --query 'Arn' --output text

# Content-type matters: without it S3 serves the file as
# application/octet-stream and the browser downloads it
# instead of playing it in the page.
echo "==> uploading videos"
aws s3 sync "$SRC" "s3://$BUCKET/video/" \
  --exclude "*" --include "*.mp4" \
  --content-type "video/mp4" \
  --cache-control "public, max-age=604800"

echo "==> uploading poster images"
aws s3 sync "$SRC" "s3://$BUCKET/video/" \
  --exclude "*" --include "*.jpg" \
  --content-type "image/jpeg" \
  --cache-control "public, max-age=604800"

# The filenames stay the same when you re-render, so a cached copy
# would keep serving the old cut. Clear it.
echo "==> clearing the CDN cache for /video/*"
ID=$(aws cloudfront create-invalidation --distribution-id "$DIST_ID" \
       --paths "/video/*" --query 'Invalidation.Id' --output text)
aws cloudfront wait invalidation-completed --distribution-id "$DIST_ID" --id "$ID"
echo "    invalidation $ID complete"

echo
echo "==> checking one file is really live"
CODE=$(curl -fsS -o /dev/null -w '%{http_code}' "$SITE_URL/video/scenario1.mp4" || echo 000)
TYPE=$(curl -fsSI "$SITE_URL/video/scenario1.mp4" 2>/dev/null \
         | tr -d '\r' | awk -F': ' 'tolower($1)=="content-type"{print $2}')
echo "    scenario1.mp4 -> http $CODE, content-type: ${TYPE:-unknown}"

if [ "$CODE" = "200" ]; then
  echo
  echo "DONE. The videos are live:"
  echo "  $SITE_URL/#/p1   $SITE_URL/#/p2"
  echo "  $SITE_URL/#/p3   $SITE_URL/#/p4"
else
  echo
  echo "WARNING: the file did not come back 200. Give the CDN a minute and re-check."
  exit 1
fi
