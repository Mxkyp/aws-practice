#!/usr/bin/env bash
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
BUCKET=${LAMBDA_BUCKET:-$(terraform -chdir="$REPO/infra" output -raw lambda_bucket_name)}
VERSION=${VERSION:-$(git -C "$REPO" describe --always --dirty)}
BUILD="$REPO/build"
mkdir -p "$BUILD"

DEPS="$BUILD/deps/python"
rm -rf "$BUILD/deps"
uv export --quiet --frozen --no-dev --no-hashes --no-emit-project -o "$BUILD/requirements.txt"
uv pip install --quiet --target "$DEPS" -r "$BUILD/requirements.txt" \
  --python-platform x86_64-manylinux2014 --python-version 3.12
cp -r "$REPO/lib/shows" "$DEPS/"

for fn in "$@"; do
  zip_path="$BUILD/$fn.zip"
  key="$fn/$VERSION.zip"

  rm -f "$zip_path"
  (cd "$REPO/functions/$fn" && zip -qr "$zip_path" . -x '__pycache__/*')
  (cd "$DEPS" && zip -qr "$zip_path" . -x '*__pycache__*' 'bin/*' '.lock')
  aws s3 cp "$zip_path" "s3://$BUCKET/$key" --quiet
  echo "uploaded s3://$BUCKET/$key"

  aws lambda update-function-code --function-name "$fn" --s3-bucket "$BUCKET" --s3-key "$key" --query CodeSha256 --output text
  aws lambda wait function-updated --function-name "$fn"

  echo "deployed $fn @ $VERSION"
done
