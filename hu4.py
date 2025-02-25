import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from io import BytesIO, StringIO

SOURCE_BUCKET = "datalakecrypto"
DESTINATION_BUCKET = "datalakecrypto-plata"
PREFIX = "crypto_data/"  # Si quieres filtrar por carpeta/prefijo, p. ej. "carpeta/", sino déjalo vacío
AWS_REGION = "eu-south-2"  # Cambia a tu región de AWS
CREDENTIALS_FILE = "./credentials.txt"
def main():
    lineas = []
    with open(CREDENTIALS_FILE,"r") as file:
        for line in file:
            lineas.append(line.strip())
    aws_access_key_id = lineas[0]
    aws_secret_access_key = lineas[1]
    aws_session_token = lineas[2]
    # Inicializar el cliente de AWS Glue
    s3 = boto3.client('s3', region_name=AWS_REGION,
                            aws_access_key_id = aws_access_key_id,
                            aws_secret_access_key = aws_secret_access_key,
                            aws_session_token = aws_session_token
                            )

    # Listar objetos en el bucket origen
    response = s3.list_objects_v2(Bucket=SOURCE_BUCKET, Prefix=PREFIX)

    if 'Contents' not in response:
        print("No se encontraron archivos en el bucket de origen con el prefijo indicado.")
        return
    # print(response["Contents"])
    for obj in response['Contents']:
        key = obj['Key']
        if key.endswith("/"):
            # Si es un "directorio" o carpeta vacía en S3, lo ignoramos
            continue
        
        # Obtener el archivo desde S3
        print(f"Procesando {key}...")
        s3_object = s3.get_object(Bucket=SOURCE_BUCKET, Key=key)

        # Suponiendo que el archivo sea un CSV; lo cargamos en un DataFrame
        csv_data = s3_object['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_data))

        # Convertimos el DataFrame a formato Parquet en memoria
        table = pa.Table.from_pandas(df)
        parquet_buffer = BytesIO()
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)

        # Construimos el nombre de salida (cambiando la extensión a .parquet)
        # Puedes modificar la ruta o el nombre según te convenga
        destino_key = key.rsplit('.', 1)[0] + ".parquet"

        # Subimos el archivo Parquet al bucket destino
        s3.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=destino_key,
            Body=parquet_buffer.getvalue()
        )
        print(f"Archivo guardado en s3://{DESTINATION_BUCKET}/{destino_key}")

if __name__ == "__main__":
    main()