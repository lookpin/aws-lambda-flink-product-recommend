echo "S3 Bucket: $S3_BUCKET"
echo "Lambda Function Name: $LAMBDA_FUNCTION_NAME"
echo "Lambda Deployment Preference: $LAMBDA_DEPLOYMENT_PREFERENCE"
echo "GitHub Branch: $BRANCH"

if [ "$BRANCH" == "master" ]; then
    BRANCH="prod"
elif [ "$BRANCH" == "dev" ]; then
    BRANCH="staging"
fi

FUNCTION_EXISTS=$(aws lambda wait function-exists --function-name ${LAMBDA_FUNCTION_NAME}-${BRANCH})
EXIT_STATUS=$?
if [ $EXIT_STATUS -ne 0 ]; then
  echo "The function doesn't exist yet. Creating it..."
  TARGET_LAMBDA_FUNCTION_VERSION=1
  echo "Target Version: ${TARGET_LAMBDA_FUNCTION_VERSION}"
else
  CURRENT_LAMBDA_FUNCTION_VERSION=$(aws lambda list-versions-by-function --function-name ${LAMBDA_FUNCTION_NAME}-${BRANCH} --query "Versions[-1].[Version]" | grep -o -E '[0-9]+')
  echo "New Current Version: ${CURRENT_LAMBDA_FUNCTION_VERSION}"
  ((CURRENT_LAMBDA_FUNCTION_VERSION++))
  TARGET_LAMBDA_FUNCTION_VERSION=${CURRENT_LAMBDA_FUNCTION_VERSION}
  echo "tried incrementing"
  echo "Target Version: ${TARGET_LAMBDA_FUNCTION_VERSION}"
fi

TARGET_LAMBDA_FUNCTION_CODE="${LAMBDA_FUNCTION_NAME}_v${TARGET_LAMBDA_FUNCTION_VERSION}.zip"

python3 -m pip install -r requirements.txt -t ./package

cd package

zip -r ../${TARGET_LAMBDA_FUNCTION_CODE} .

cd ../

pwd
ls
cd function
zip -u ../${TARGET_LAMBDA_FUNCTION_CODE} psycopg2/*.py
zip -u ../${TARGET_LAMBDA_FUNCTION_CODE} psycopg2/*.so

mv *.py ../
cd ..
zip -g ${TARGET_LAMBDA_FUNCTION_CODE} *.py

aws s3 cp ${TARGET_LAMBDA_FUNCTION_CODE} s3://${S3_BUCKET}/${BRANCH}/${TARGET_LAMBDA_FUNCTION_CODE}

cat >template.yaml <<EOM
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  LambdaFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: ${LAMBDA_FUNCTION_NAME}-${BRANCH}
      Handler: lambda_function.lambda_handler
      Runtime: python3.8
      CodeUri: s3://${S3_BUCKET}/${BRANCH}/${TARGET_LAMBDA_FUNCTION_CODE}
      AutoPublishAlias: default
      Timeout: 30
      DeploymentPreference:
        Enabled: True
        Type: ${LAMBDA_DEPLOYMENT_PREFERENCE}
EOM
cat template.yaml