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
    mensaje=transferir_local_boto3(clave,origin_disc)
    return mensaje

def descargar(event,cotext):
    # for key, value in sorted(botocore.exceptions.__dict__.items()):
    #     if isinstance(value, type):
    #         print(key)
    clave=CLAVE_ENCRYT
    temp_disc=DISCO_DESTINO
    mensaje=descargar_local_boto3(clave,temp_disc)
    return mensaje

# Funciones para encriptar
def transferir_local_boto3(key,pathOrigin)-> list:

    # iniciamos la funcion para conectar al bucket s3
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_URL,
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            region_name=REGION_NAME)
    try:
        bucket=BUCKET
        s3.head_bucket(Bucket=bucket)
        # list=s3.list_objects(Bucket=bucket)['Contents']
        if not isinstance(boto3.client('s3'), botocore.client.BaseClient):
            return {"status": "error", "message":"error.handler.descargar_local_boto3", "messageDetail":"Error en la conexion"}
        
        if not os.path.isdir(pathOrigin):
            return {"status": "error", "message":"error.handler.transferir_local_boto3", "messageDetail":"La carpeta de origen ("+pathOrigin+") no existe."}
        
        else:
            # generamos el hash con la clave
            clave=generar_claveDome(key)
            if type(clave).__name__ !='bytes':
                return clave
            # obtenemos los archivos de la carpeta de origen y recorremos para subir al bucket s3
            contenidos=os.listdir(pathOrigin)
            if len(contenidos)==0:
                return {"status": "error", "message":"error.handler.transferir_local_boto3", "messageDetail":"No se encontraron archivos para subir en el origen({})".format(pathOrigin)}
                
            hubo_error=False
            rpt=True
            lista_archivos_no_subidos=[]
            for elemento in contenidos:
                # if not hubo_error:
                    # encriptamos el archivo}
                    encripted_archive_url=encriptar_archivoAESDome(pathOrigin,elemento,clave)
                    # print(encripted_archive_url)
                    if type(encripted_archive_url).__name__=='str':
                    # subimos los archivos al bucker s3
                        s3.upload_file(pathOrigin+"/"+encripted_archive_url, bucket, encripted_archive_url)
                        
                        results = s3.list_objects(Bucket=bucket, Prefix=encripted_archive_url)
                        # se_subio = list(bucket_temp.objects.filter(Prefix=encripted_archive_url))
                        if 'Contents' not in results:
                            lista_archivos_no_subidos.append({"archivo":elemento,"motivo":"No se subio el archivo"})
                        os.remove(pathOrigin+"/"+encripted_archive_url)
                    else:
                        lista_archivos_no_subidos.append({"archivo":elemento,"motivo":"No se encripto el archivo"})
                        # rpt= encripted_archive_url
                        # hubo_error=True
                        # break
                # borramos el archivo temporal

            # if hubo_error:
            #      return rpt
            # else:
            print("[success.handler.transferir_local_boto3]:archivos encriptados y subidos")
            return {"status": "success", "message":"success.handler.transferir_local_boto3", "messageDetail":"archivos encriptados y subidos","errores":"{}".format(lista_archivos_no_subidos)}
    
    except  botocore.exceptions.ConnectionError as ex:
        # print(ex)
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"Error de conexion"}
    
    except  botocore.exceptions.NoCredentialsError as ex:
        # print(ex)
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"Error de credenciales"}
    
    except  s3.exceptions.NoSuchBucket as ex:
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except  s3.exceptions.NoSuchKey as ex:
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"No se encontro el archivo en el bucket({})".format(BUCKET)}
    
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 403:
            return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"El bucket({}) esta en modo privado".format(BUCKET)}
    
        elif error_code == 404:
            return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except Exception as ex:
        print(ex.args)
        return {"status": "error", "message": "error.handler.transferir_local_boto3", "messageDetail":ex.args}

def descargar_local_boto3(key1,destino):
    s3 = boto3.client('s3', endpoint_url=ENDPOINT_URL,
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            region_name=REGION_NAME)
        
    try:
        clave=generar_claveDome(key1)
        if type(clave).__name__ !='bytes':
            return clave

        bucket=BUCKET
        s3.head_bucket(Bucket=bucket)
        if not isinstance(boto3.client('s3'), botocore.client.BaseClient):
            return {"status": "success", "message":"success.handler.descargar_local_boto3", "messageDetail":"Error en la conexion"}
            
        if not os.path.isdir(destino):
            return {"status": "success", "message":"success.handler.descargar_local_boto3", "messageDetail":"La carpeta de destino ("+destino+") no existe."}
    
        else:
            list=s3.list_objects(Bucket=bucket)['Contents']
            if len(list)==0:
                return {"status": "success", "message":"success.handler.descargar_local_boto3", "messageDetail":"No se encontraron archivos para descargar del bucket({})".format(bucket)}
            # hubo_error=False
            # rpt=True
            lista_archivos_erroneos=[]
            for key in list:
                # if not hubo_error:
                    s3.download_file(bucket, key['Key'], destino+key['Key'])
                    if os.path.isfile(destino+key['Key']):
                        rpt=desencriptar_archivoAESDome(destino+key['Key'],clave)
                        if rpt is not True:
                            # os.remove(destino+key['Key'])
                            # hubo_error=True
                            # break
                            lista_archivos_erroneos.append({"archivo":key['Key'],"motivo":"El archivo se descargo, pero no se desencripto(archivo corrupto o contrasenia invalida)"})                 
                    else:
                        lista_archivos_erroneos.append({"archivo":key['Key'],"motivo":"El archivo no se descargo"})
                        # raise Exception("No existe el archivo en({0})".format(destino+'/'+key['key']) )
            # if hubo_error:
            #      return rpt

            # else:
            return {"status": "success", "message":"success.handler.descargar_local_boto3", "messageDetail":"archivos descargados","errores":"{}".format(lista_archivos_erroneos)}
    
    except  botocore.exceptions.ConnectionError as ex:
        print(ex)
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"Error de conexion"}

    except  botocore.exceptions.NoCredentialsError as ex:
        print(ex)
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"Error de credenciales"}
    
    except  s3.exceptions.NoSuchBucket as ex:
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except  s3.exceptions.NoSuchKey as ex:
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"No se encontro el archivo en el bucket({})".format(BUCKET)}
    
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 403:
            return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"El bucket({}) esta en modo privado".format(BUCKET)}
    
        elif error_code == 404:
            return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":"El bucket({}) no existe".format(BUCKET)}
    
    except Exception as ex:
        # return ex
        return {"status": "error", "message": "error.handler.descargar_local_boto3", "messageDetail":ex.args}

def generar_claveDome(key):
    try: 
        dome= AESDome('','')
        clave=dome.generarKey(key)
        with open("clave.key","wb") as archivo_clave:
            archivo_clave.write(clave)
        return clave
    except Exception as ex:
        print(ex.args)
        return {"status": "error", "message": "error.handler.generar_claveDome", "messageDetail":"Error al generar la clave."}

def encriptar_archivoAESDome(ubicacion,nom_archivo,clave):
    try:
        aesDome=AESDome(clave,'')
        file=open(ubicacion+"/"+nom_archivo,"rb")
        archivo_info=file.read()
        file.close()    
        encrypted_data=aesDome.encritar(archivo_info)
        if type(encrypted_data).__name__ =='bytes':
            new_url=datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
            new_url=str(new_url+"_"+nom_archivo)
            file_out=open(ubicacion+"/"+new_url,"wb")
            file_out.write(aesDome.iv)
            file_out.write(encrypted_data)
            file_out.close()
            return new_url
        else:
            os.remove(ubicacion+"/"+nom_archivo)
            return encrypted_data

    except Exception as ex:
        print(ex.args)
        return {"status": "error", "message": "error.handler.encriptar_archivoAESDome", "messageDetail":"{}".format(ex)}

def desencriptar_archivoAESDome(nom_archivo,clave) :
    try:
        file_in= open(nom_archivo,"rb")
        iv= file_in.read(16) 
        encrypted_info=file_in.read()
        file_in.close()
        aesDome=AESDome(clave,iv)
        decrypted_data=aesDome.desencritar(encrypted_info)
        
        # print(type(decrypted_data).__name__)
        if type(decrypted_data).__name__ =='bytes':
            file_out=open(nom_archivo,"wb")
            file_out.write(decrypted_data)
            file_out.close()
            return True 
        else:
            return decrypted_data
        
    except Exception as ex:
        # return False
        # print(ex.args)
        # return ex
        return {"status": "error", "message": "error.handler.desencriptar_archivoAESDome", "messageDetail":"{}".format(ex)}

# def hello(event, context):
#     body = {
#         "message": "Ejecucion corr!",
#         "input": event
#     }

#     response = {
#         "statusCode": 200,
#         "body": json.dumps(body,default = myconverter)
#     }

#     return response
# def myconverter(o):
#     if isinstance(o, datetime.datetime):
#         return o.__str__()
#     # Use this code if you don't use the http event with the LAMBDA-PROXY
#     # integration
#     """
#     return {
#         "message": "Go Serverless v1.0! Your function executed successfully!",
#         "event": event
#     }
#     """