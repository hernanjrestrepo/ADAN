# Importar las bibliotecas necesarias
import boto3
import json
import os

# Crear el cliente de Lambda
iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')

# Nombre del clon que se va a crear
clone_name = "adan_clone_9"

# Definir la función lambda_handler
def lambda_handler(event, context):
    try:
        # Definir la configuración del clon
        response = lambda_client.create_function(
            FunctionName=clone_name,
            Runtime='python3.9',
            Role=os.environ['LAMBDA_ROLE_ARN'],
            Handler='lambda_function.lambda_handler',
            Code={
                'S3Bucket': 'adan-execution-results',
                'S3Key': 'lambda_function.zip'
            },
            Description='Clon automático de la función Lambda de ADAN',
            Timeout=15,
            MemorySize=128,
            Publish=True,
        )
        return {
            'statusCode': 200,
            'body': json.dumps(f"Clon creado exitosamente: {clone_name}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al crear el clon: {str(e)}")
        }
