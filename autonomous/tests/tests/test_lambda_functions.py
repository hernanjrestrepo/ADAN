import unittest
import boto3
from botocore.exceptions import ClientError

class TestLambdaFunction(unittest.TestCase):
    def test_lambda_exists(self):
        lambda_client = boto3.client('lambda', region_name='us-east-2')
        try:
            response = lambda_client.get_function(FunctionName='adan_clone_manager_v2')
            self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], 200)
        except ClientError as e:
            self.fail(f"Lambda function not found: {e}")

    def test_sample(self):
        self.assertEqual(2 + 2, 4)

if __name__ == '__main__':
    unittest.main()
