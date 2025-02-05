#!/usr/bin/env python3

import os
import sys
import boto3

def main():
    # ------------------------------------------------------------------------------
    # 1. CONFIGURACIONES
    # ------------------------------------------------------------------------------
    # Región de AWS para España (eu-south-2)
    AWS_REGION = "eu-south-2"
    
    # Nombre del bucket (cámbialo si lo prefieres)
    BUCKET_NAME = "crypto-data"
    
    # Carpeta local con tus subdirectorios y archivos ya existentes
    LOCAL_FOLDER = "crypto_data"

    # ------------------------------------------------------------------------------
    # 2. CREAR EL BUCKET EN S3 (si no existe)
    # ------------------------------------------------------------------------------
    s3_client = boto3.client("s3", region_name=AWS_REGION)

    try:
        s3_client.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
        )
        print(f"Bucket '{BUCKET_NAME}' creado exitosamente en la región '{AWS_REGION}'.")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"El bucket '{BUCKET_NAME}' ya existe y es tuyo. Se omite la creación.")
    except s3_client.exceptions.BucketAlreadyExists:
        print(f"El bucket '{BUCKET_NAME}' ya existe y no puede ser creado (no es tuyo). Usa otro nombre.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al crear el bucket: {e}")
        sys.exit(1)

    # ------------------------------------------------------------------------------
    # 3. RECORRER LA CARPETA LOCAL Y SUBIR ARCHIVOS A S3
    # ------------------------------------------------------------------------------
    if not os.path.isdir(LOCAL_FOLDER):
        print(f"La carpeta local '{LOCAL_FOLDER}' no existe. Verifica tu ruta.")
        sys.exit(1)

    for root, dirs, files in os.walk(LOCAL_FOLDER):
        for filename in files:
            local_path = os.path.join(root, filename)
            
            # Generar la ruta dentro del bucket (manteniendo la estructura local)
            # Obtenemos la ruta relativa desde la carpeta LOCAL_FOLDER
            relative_path = os.path.relpath(local_path, LOCAL_FOLDER)
            
            # La "key" en S3 es la ruta donde se guardará el archivo
            s3_key = os.path.join(LOCAL_FOLDER, relative_path)

            try:
                s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
                print(f"Subido: {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
            except Exception as e:
                print(f"Error al subir {local_path}: {e}")

    print("Proceso finalizado. Todos los archivos han sido subidos a S3.")

if __name__ == "__main__":
    main()

