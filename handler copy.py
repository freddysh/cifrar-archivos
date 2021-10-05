from AESDome import AESDome
import json
import os
import boto3
import datetime

def hello(event, context):
    body = {
        "message": "Ejecucion corr!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body,default = myconverter)
    }

    return response
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

def subir(event,cotext):
    clave='mi_clave_2021'
    origin_disc='/home/fsilva/disco_a'
    mensaje=transferir_local_boto3(clave,origin_disc)
    body = {
        "message": mensaje
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

def descargar(event,cotext):
    clave='mi_clave_2021'
    destiy_disc=''
    mensaje=descargar_local_boto3(clave)
    body = {
        "message": mensaje
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response

# Funciones para encriptar
def transferir_local_boto3(key,pathOrigin)-> list:

    try:
        # configuramos la credenciales del bucket s3
        aws_access_key_id='AKIARUFHRLUFDWPLDMSP'
        aws_secret_access_key_id='QxdTGwmnbggZnYk4umoVJNJqATqFI06qY+9vmbEp'
        region_name='us-east-2'

        # iniciamos la funcion para conectar al bucket s3
        s3=boto3.resource('s3')

        # recuperamos la carpeta de origen
        # pathOrigin='/home/fsilva/disco_a'
        
        # definimos una lista para garegar los archivos subidos
        archivos:list=list()
        if not os.path.isdir(pathOrigin):
            raise Exception('La carpeta('+pathOrigin+') no existe')
        else:
            # generamos el hash con la clave
            clave=generar_claveDome(key)
            # obtenemos los archivos de la carpeta de origen y recorremos para subir al bucket s3
            contenidos=os.listdir(pathOrigin)
            for elemento in contenidos:
                # encriptamos el archivo}
                encripted_archive_url=encriptar_archivoAESDome(pathOrigin,elemento,clave)
                # subimos los archivos al bucker s3
                s3.Object('freddy2021',encripted_archive_url).upload_file(pathOrigin+"/"+encripted_archive_url) 
                # borramos el archivo temporal
                os.remove(pathOrigin+"/"+encripted_archive_url)
                archivos.append({"name":encripted_archive_url})
            return archivos
    except Exception as ex:
        print("Ha habido una excepción", type(ex))

def descargar_local_boto3(key1,destino)-> list:
    try:
        # configuramos la credenciales del bucket s3
        aws_access_key_id='AKIARUFHRLUFDWPLDMSP'
        aws_secret_access_key_id='QxdTGwmnbggZnYk4umoVJNJqATqFI06qY+9vmbEp'
        region_name='us-east-2'

        # clave=cargar_clave()
        clave=generar_claveDome(key1)
        # iniciamos la funcion para conectar al bucket s3
        s3=boto3.client('s3')
        # destino='discoc/'
        if not os.path.isdir(destino):
            raise Exception('La carpeta('+destino+') no existe')
        else:
            # definimos una lista para garegar los archivos subidos
            archivos_des =[]
            list=s3.list_objects(Bucket='freddy2021')['Contents']
            for key in list:
                s3.download_file('freddy2021', key['Key'], destino+key['Key'])
                desencriptar_archivoAESDome(destino+key['Key'],clave)
                archivos_des.append({"name":key['Key']})
            return archivos_des
    except Exception as ex:
        print("Ha habido una excepción", type(ex))

def cargar_clave():
    return open("clave.key","rb").read()

def generar_claveDome(key):
    dome= AESDome('','')
    clave=dome.generarKey(key)
    with open("clave.key","wb") as archivo_clave:
        archivo_clave.write(clave)
    return clave

def encriptar_archivoAESDome(ubicacion,nom_archivo,clave) -> str:
    aesDome=AESDome(clave,'')
    with open(ubicacion+"/"+nom_archivo,"rb") as file:
        archivo_info=file.read()
    encrypted_data=aesDome.encritar(archivo_info)
    new_url=datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    new_url=new_url+"_"+nom_archivo
    file_out=open(ubicacion+"/"+new_url,"wb")
    file_out.write(aesDome.iv)
    file_out.write(encrypted_data)
    file_out.close()
    return new_url

def desencriptar_archivoAESDome(nom_archivo,clave):
    file_in= open(nom_archivo,"rb")
    iv= file_in.read(16) 
    encrypted_info=file_in.read()
    file_in.close()
    aesDome=AESDome(clave,iv)
    decrypted_data=aesDome.desencritar(encrypted_info)
    with open(nom_archivo,"wb") as file:
        file.write(decrypted_data)