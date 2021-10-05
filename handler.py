from typing import Dict
from AESDome import AESDome
import json
import os
import boto3
import botocore
import datetime
import botocore.exceptions
from variables import CLAVE_ENCRYT,BUCKET,ENDPOINT_URL,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,REGION_NAME,DISCO_ORIGEN,DISCO_DESTINO

def subir(event,cotext):
    clave=CLAVE_ENCRYT
    origin_disc=DISCO_ORIGEN
    mensaje=encriptar_transferir(clave,origin_disc)
    return mensaje

def descargar(event,cotext):
    clave=CLAVE_ENCRYT
    destino=DISCO_DESTINO
    mensaje=decriptar_descargar(clave,destino)
    return mensaje

# Funciones para encriptar
def encriptar_transferir(key,origin_disc):
    ubicacion_mensaje="error.handler.encriptar_transferir"
    error_mensaje="error"
    # iniciamos la funcion para conectar al bucket s3
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_URL,
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            region_name=REGION_NAME)
    
    try:
        s3.head_bucket(Bucket=BUCKET)
        if not isinstance(boto3.client('s3'), botocore.client.BaseClient):
            return {"status": error_mensaje, "message":ubicacion_mensaje, "messageDetail":"Error en la conexion"}
        
        if not os.path.isdir(origin_disc):
            return {"status": error_mensaje, "message":ubicacion_mensaje, "messageDetail":"La carpeta de origen ("+origin_disc+") no existe."}
        
        else:
            # generamos el hash con la clave
            clave=generar_clave_dome(key)
            if type(clave).__name__ !='bytes':
                return clave
            # obtenemos los archivos de la carpeta de origen y recorremos para subir al bucket s3
            contenidos=os.listdir(origin_disc)
            if len(contenidos)==0:
                return {"status": error_mensaje, "message":ubicacion_mensaje, "messageDetail":"No se encontraron archivos para subir en el origen({})".format(origin_disc)}
                
            lista_archivos_no_subidos=[]
            for elemento in contenidos:
                    # encriptamos el archivo
                    encripted_archive_url=encriptar_archivo_aes_dome(origin_disc,elemento,clave)
                    
                    if type(encripted_archive_url).__name__=='str':
                    # subimos los archivos al bucker s3
                        s3.upload_file(origin_disc+"/"+encripted_archive_url, BUCKET, encripted_archive_url)
                        results = s3.list_objects(Bucket=BUCKET, Prefix=encripted_archive_url)
                        if 'Contents' not in results:
                            lista_archivos_no_subidos.append({"archivo":elemento,"motivo":"No se subio el archivo"})
                        os.remove(origin_disc+"/"+encripted_archive_url)
                    else:
                        lista_archivos_no_subidos.append({"archivo":elemento,"motivo":"No se encripto el archivo"})
                
            print("[success.handler.transferir_local_boto3]:archivos encriptados y subidos")
            return {"status": "success", "message":"success.handler.transferir_local_boto3", "messageDetail":"archivos encriptados y subidos","errores":"{}".format(lista_archivos_no_subidos)}
    
    except  botocore.exceptions.ConnectionError as ex:
        # print(ex)
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"Error de conexion"}
    
    except  botocore.exceptions.NoCredentialsError as ex:
        # print(ex)
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"Error de credenciales"}
    
    except  s3.exceptions.NoSuchBucket as ex:
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except  s3.exceptions.NoSuchKey as ex:
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"No se encontro el archivo en el bucket({})".format(BUCKET)}
    
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 403:
            return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"El bucket({}) esta en modo privado".format(BUCKET)}
    
        elif error_code == 404:
            return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except Exception as ex:
        print(ex.args)
        return {"status": error_mensaje, "message": "error.handler.transferir_local_boto3", "messageDetail":ex.args}

def decriptar_descargar(key1,destino):
    ubicacion_mensaje="error.handler.decriptar_descargar"
    error_mensaje="error"
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_URL,
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            region_name=REGION_NAME)
    try:
        clave=generar_clave_dome(key1)
        if type(clave).__name__ !='bytes':
            return clave

        s3.head_bucket(Bucket=BUCKET)
        if not isinstance(boto3.client('s3'), botocore.client.BaseClient):
            return {"status": error_mensaje, "message":ubicacion_mensaje, "messageDetail":"Error en la conexion"}
            
        if not os.path.isdir(destino):
            return {"status": error_mensaje, "message":ubicacion_mensaje, "messageDetail":"La carpeta de destino ("+destino+") no existe."}
    
        else:
            lista_de_archivos=s3.list_objects(Bucket=BUCKET)['Contents']
            if len(lista_de_archivos)==0:
                return {"status": error_mensaje, "message":ubicacion_mensaje, "messageDetail":"No se encontraron archivos para descargar del bucket({})".format(BUCKET)}
           
            lista_archivos_erroneos=[]
            for key in lista_de_archivos:
                    s3.download_file(BUCKET, key['Key'], destino+key['Key'])
                    if os.path.isfile(destino+key['Key']):
                        rpt=desencriptar_archivo_aes_dome(destino+key['Key'],clave)
                        if rpt is not True:
                            lista_archivos_erroneos.append({"archivo":key['Key'],"motivo":"El archivo se descargo, pero no se desencripto(archivo corrupto o contrasenia invalida)"})                 
                    else:
                        lista_archivos_erroneos.append({"archivo":key['Key'],"motivo":"El archivo no se descargo"})
            
            return {"status": "success", "message":"success.handler.descargar_local_boto3", "messageDetail":"archivos descargados","errores":"{}".format(lista_archivos_erroneos)}
    
    except  botocore.exceptions.ConnectionError as ex:
        print(ex)
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"Error de conexion"}

    except  botocore.exceptions.NoCredentialsError as ex:
        print(ex)
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"Error de credenciales"}
    
    except  s3.exceptions.NoSuchBucket as ex:
        print(ex)
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except  s3.exceptions.NoSuchKey as ex:
        print(ex)
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"No se encontro el archivo en el bucket({})".format(BUCKET)}
    
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 403:
            return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"El bucket({}) esta en modo privado".format(BUCKET)}
    
        elif error_code == 404:
            return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except Exception as ex:
        print(ex)
        return {"status": error_mensaje, "message": ubicacion_mensaje, "messageDetail":ex.args}

def generar_clave_dome(key):
    try: 
        dome= AESDome('','')
        clave=dome.generar_clave(key)
        return clave
    except Exception as ex:
        print(ex.args)
        return {"status": "error", "message": "error.handler.generar_claveDome", "messageDetail":"Error al generar la clave."}

def encriptar_archivo_aes_dome(ubicacion,nom_archivo,clave):
    try:
        aes_dome=AESDome(clave,'')
        file=open(ubicacion+"/"+nom_archivo,"rb")
        archivo_info=file.read()
        file.close()    
        encrypted_data=aes_dome.encritar(archivo_info)
        if type(encrypted_data).__name__ =='bytes':
            new_url=datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
            new_url=str(new_url+"_"+nom_archivo)
            file_out=open(ubicacion+"/"+new_url,"wb")
            file_out.write(aes_dome.iv)
            file_out.write(encrypted_data)
            file_out.close()
            return new_url
        else:
            # os.remove(ubicacion+"/"+nom_archivo)
            print(encrypted_data)
            return encrypted_data

    except Exception as ex:
        print(ex.args)
        return {"status": "error", "message": "error.handler.encriptar_archivo_aes_dome", "messageDetail":"{}".format(ex)}

def desencriptar_archivo_aes_dome(nom_archivo,clave) :
    try:
        file_in= open(nom_archivo,"rb")
        iv= file_in.read(16) 
        encrypted_info=file_in.read()
        file_in.close()
        aes_dome=AESDome(clave,iv)
        decrypted_data=aes_dome.desencritar(encrypted_info)
        
        if type(decrypted_data).__name__ =='bytes':
            file_out=open(nom_archivo,"wb")
            file_out.write(decrypted_data)
            file_out.close()
            return True 
        else:
            return decrypted_data
        
    except Exception as ex:
        return ex
        return {"status": "error", "message": "error.handler.desencriptar_archivo_aes_dome", "messageDetail":"{}".format(ex)}