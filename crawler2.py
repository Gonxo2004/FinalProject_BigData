import boto3

# Configuración
AWS_REGION = "eu-south-2"  # Cambia a tu región de AWS
DATABASE_NAME = "trade_data_imat3a03"  # Nombre de la base de datos
CRAWLER_NAME = "trade_data_crawler"
S3_TARGET_PATH = "s3://datalakecrypto/crypto_data/"  # Cambia con tu bucket
IAM_ROLE = "arn:aws:iam::205930633313:role/service-role/AWSGlueServiceRole-CrawlerRole"  # Cambia con tu rol de Glue
CREDENTIALS_FILE = "./credentials.txt"

lineas = []
with open(CREDENTIALS_FILE,"r") as file:
    for line in file:
        lineas.append(line.strip())
aws_access_key_id = lineas[0]
aws_secret_access_key = lineas[1]
aws_session_token = lineas[2]
# Inicializar el cliente de AWS Glue
glue_client = boto3.client('glue', region_name=AWS_REGION,
                           aws_access_key_id = aws_access_key_id,
                           aws_secret_access_key = aws_secret_access_key,
                           aws_session_token = aws_session_token
                           )

# 1. Crear la base de datos en AWS Glue Data Catalog
def create_database():
    try:
        glue_client.create_database(
            DatabaseInput={
                'Name': DATABASE_NAME,
                'Description': 'Base de datos para almacenar metadatos de datos históricos en S3'
            }
        )
        print(f"Base de datos '{DATABASE_NAME}' creada.")
    except glue_client.exceptions.AlreadyExistsException:
        print(f"La base de datos '{DATABASE_NAME}' ya existe.")

# 2. Crear el AWS Glue Crawler
def create_crawler():
    try:
        glue_client.create_crawler(
            Name=CRAWLER_NAME,
            Role=IAM_ROLE,
            DatabaseName=DATABASE_NAME,
            Targets={'S3Targets': [{'Path': S3_TARGET_PATH}]},
            TablePrefix="trade_data_"
        )
        print(f"Crawler '{CRAWLER_NAME}' creado.")
    except glue_client.exceptions.AlreadyExistsException:
        print(f"El crawler '{CRAWLER_NAME}' ya existe.")

# 3. Ejecutar el Crawler
def start_crawler():
    glue_client.start_crawler(Name=CRAWLER_NAME)
    print(f"Crawler '{CRAWLER_NAME}' iniciado.")

# Ejecutar las funciones
create_database()
create_crawler()
start_crawler()
