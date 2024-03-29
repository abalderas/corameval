#!/usr/bin/python
# -*- coding: latin-1 -*-
from flask import Flask, render_template, url_for, request, jsonify, json, session
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from flask_bcrypt import bcrypt
from datetime import datetime
from difflib import SequenceMatcher

# librerías para la figura
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt; plt.rcdefaults()
#import numpy as np
#import matplotlib.pyplot as plt

app = Flask(__name__)

# Database connection

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'config/config.json')

if os.path.exists(file_path):
    # Cargar la configuración desde un archivo JSON
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)

app.config.from_mapping(config_data)

#app.config.from_json('config/config.json')
mongo = PyMongo(app)

# Session
app.secret_key = 'mysecretkey'

# Login
@app.route('/login', defaults={'error': 0})
@app.route('/login/<error>')
def login(error):
    
    if 'username' in session:
        return Index()
        #return 'logged as ' + session['username']

    return render_template('login.html', error = error)

# https://www.youtube.com/watch?v=vVx1737auSE

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    if 'universidad' in session:
        session.pop('universidad')
    if 'admin' in session:
        session.pop('admin')

    return login(0)

@app.route('/access', methods=['POST'])
def access():   
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})    

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            if 'universidad' in login_user:
                session['universidad'] = login_user['universidad']
            if 'admin' in login_user:
                session['admin'] = login_user['admin']
            return Index()
        return login(1)
    return login(2)

# Función privada creacion clave usuarios
@app.route('/password/<clave>')
def password(clave):
    encriptada = bcrypt.hashpw(clave.encode('utf8'), bcrypt.gensalt())
    return encriptada

@app.route('/')
def Index():
    if 'username' not in session:
        return login(0)

    if 'universidad' in session:
        documents_unis = mongo.db.asignaturas.distinct("universidad", {"universidad": session['universidad']})
    else:
        documents_unis = mongo.db.asignaturas.distinct("universidad")
    
    if documents_unis:
        return render_template('index.html', universidades = documents_unis, selected = {'universidad': ""})
    
    return render_template('error.html', msj = 'Sin datos de esta universidad')
    # -------------------------------------------------------------------------
    # Conjunto de funciones que cargan mediante AJAX los desplegables asociados
    # -------------------------------------------------------------------------

@app.route('/listing_areas', methods=['POST'])
def listing_areas():
    universidad = request.form['universidad']

    documents_area = mongo.db.asignaturas.distinct("area", {"universidad": universidad}) 

    return jsonify(documents_area)


@app.route('/listing_degrees', methods=['POST'])
def listing_degrees():
    universidad = request.form['universidad']
    area = request.form['area']

    documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": universidad, "area": area}) 

    return jsonify(documents_titu)

@app.route('/listing_niveles1', methods=['POST'])
def listing_niveles1():
    universidad = request.form['universidad']
    area = request.form['area']
    degree = request.form['degree']

    documents_cour = mongo.db.asignaturas.distinct("nivel1", {"universidad": universidad, "area": area, "titulo": degree}) 

    return jsonify(documents_cour)

@app.route('/listing_niveles2', methods=['POST'])
def listing_niveles2():
    universidad = request.form['universidad']
    area = request.form['area']
    degree = request.form['degree']
    nivel1 = request.form.get('nivel1','')

    documents_cour = mongo.db.asignaturas.distinct("nivel2", {"universidad": universidad, "area": area, "titulo": degree, "nivel1": nivel1}) 

    return jsonify(documents_cour)


@app.route('/listing_courses', methods=['POST'])
def listing_courses():
    universidad = request.form['universidad']
    area = request.form['area']
    degree = request.form['degree']
    nivel1 = request.form.get('nivel1','')
    nivel2 = request.form.get('nivel2','')

    documents_cour = mongo.db.asignaturas.distinct("asignatura", {"universidad": universidad, "area": area, "titulo": degree, "nivel1": nivel1, "nivel2": nivel2}) 

    return jsonify(documents_cour)

    
@app.route('/listing_details', methods=['POST'])
def listing_details():
    universidad = request.form['universidad']
    area = request.form['area']
    degree = request.form['degree']
    nivel1 = request.form.get('nivel1','')
    nivel2 = request.form.get('nivel2','')
    course = request.form['course']

    document_detl = mongo.db.asignaturas.find_one({"universidad": universidad, "area": area, "titulo": degree, "nivel1": nivel1, "nivel2": nivel2, "asignatura": course}, {"modalidad":1, "creditos":1, "tipo":1}) 

    data = {'tipo': document_detl.get('tipo',''), 'creditos': document_detl.get('creditos',''), 'modalidad': document_detl.get('modalidad',' ')}

    return jsonify(data)

    # -------------------------------------------------------------------------
    # Final del bloque de AJAX
    # -------------------------------------------------------------------------

@app.route('/buscar', defaults={'id': 0}, methods=['POST'])
@app.route('/buscar/<id>')
def buscar(id):
    if id != 0:
        document_detl = mongo.db.asignaturas.find_one({"_id": ObjectId(id)}, {"universidad": 1, "area": 1, "titulo": 1,
         "nivel1":1, "nivel2": 1, "asignatura": 1, "_id": 1, "modalidad":1, "creditos":1, "tipo":1})
        
        data_selected = {
            'universidad': document_detl.get('universidad',''),
            'area': document_detl.get('area',''),
            'titulo': document_detl.get('titulo',''),
            'nivel1': document_detl.get('nivel1',''),
            'nivel2': document_detl.get('nivel2',''),
            'asignatura': document_detl.get('asignatura',''),
            'modalidad': document_detl.get('modalidad',' '),
            'tipo': document_detl.get('tipo',''),
            'creditos': document_detl.get('creditos','')
            }
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": document_detl.get('universidad',''), "area": document_detl.get('area','')})
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        documents_area = mongo.db.asignaturas.distinct("area", {"universidad": document_detl.get('universidad','')})
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": document_detl.get('universidad',''), "area": document_detl.get('area','')}) 
        documents_nivel1 = mongo.db.asignaturas.distinct("nivel1", {"universidad": document_detl.get('universidad',''), "area": document_detl.get('area',''), "titulo": document_detl.get('titulo','')})
        documents_nivel2 = mongo.db.asignaturas.distinct("nivel2", {"universidad": document_detl.get('universidad',''), "area": document_detl.get('area',''), "titulo": document_detl.get('titulo',''), "nivel1": document_detl.get('nivel1','')})
        documents_cour = mongo.db.asignaturas.distinct("asignatura", {"universidad": document_detl.get('universidad',''), "area": document_detl.get('area',''), "titulo": document_detl.get('titulo',''), "nivel1": document_detl.get('nivel1',''), "nivel2": document_detl.get('nivel2','')}) 
    
        course_id = document_detl['_id']
        documents_skills = mongo.db.competencias.find({"course_id": course_id}).sort("name",1)
        documents_results = mongo.db.resultados.find({"course_id": course_id}).sort("name",1)
        documents_instruments = mongo.db.instrumentos.find({"course_id": course_id}).sort("name",1)


    else:
        data_selected = {}
        documents_skills = {}
        documents_results = {}
        documents_instruments = {}
        # Atascado en este error. Cuando lo submito en blanco (entre paréntesis la selección de universidad) 
        # Da error de area. No entiendo por qué area da error, pero si completo el area entonces no hay errores
        # Si completas solo la universidad, ya funciona bien y no casca. Pudiendo completar buscar uno a uno
        if request.form['university']!="0":
            documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": request.form['university']})
            documents_unis = mongo.db.asignaturas.distinct("universidad")
            selected_uni = request.form['university']
            
            data_selected['universidad'] = selected_uni
            documents_area = mongo.db.asignaturas.distinct("area", {"universidad": selected_uni})
            selected_area = request.form['area']
            data_selected['area'] = selected_area
            documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": selected_uni, "area": selected_area}) 
            selected_titu = request.form.get('titulo','')
            data_selected['titulo'] = selected_titu
            documents_nivel1 = mongo.db.asignaturas.distinct("nivel1", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu})
            selected_nivel1 = request.form.get('nivel1','')
            data_selected['nivel1'] = selected_nivel1
            documents_nivel2 = mongo.db.asignaturas.distinct("nivel2", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1})
            selected_nivel2 = request.form.get('nivel2','')
            data_selected['nivel2'] = selected_nivel2
            documents_cour = mongo.db.asignaturas.distinct("asignatura", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1, "nivel2": selected_nivel2})
            selected_cour = request.form.get('asignatura','')
            data_selected['asignatura'] = selected_cour
            document_detl = mongo.db.asignaturas.find_one({"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1, "nivel2": selected_nivel2, "asignatura": selected_cour}, {"modalidad": 1, "creditos":1, "tipo":1}) 
            if document_detl:
                data_selected['modalidad'] = document_detl.get('modalidad',' ')
                data_selected['tipo'] = document_detl.get('tipo','')
                data_selected['creditos'] = document_detl.get('creditos','')                
                # skills
                course_id = document_detl['_id']
                documents_skills = mongo.db.competencias.find({"course_id": course_id}).sort("name",1)
                documents_results = mongo.db.resultados.find({"course_id": course_id}).sort("name",1)
                documents_instruments = mongo.db.instrumentos.find({"course_id": course_id}).sort("name",1) 
        else:
            return Index()    
    
    return render_template('index.html', universidades = documents_unis, areas = documents_area, titulos = documents_titu, 
        niveles1 = documents_nivel1, niveles2 = documents_nivel2, asignaturas = documents_cour, selected = data_selected, 
        skills = documents_skills, results = documents_results, instruments = documents_instruments)


@app.route('/skill/<id>', defaults={'save':0})
@app.route('/skill/<id>/<save>')
def skill(id, save):
    # obtenemos id del curso
    document_skill = mongo.db.competencias.find_one({"_id": ObjectId(id)}, {"course_id":1, "name":1, "tipo": 1, 
        "correccion":1, "cognitivo":1, "factual": 1, "conceptual":1, "procedimental": 1, "metacognitivo":1,
        "estructura":1, "afectivo":1, "tecnologico":1, "colaborativo":1, "observaciones": 1, "revisiones": 1}) 
    data_course = institution(document_skill['course_id'])
    
    documents_all_skills = mongo.db.competencias.find({"course_id": document_skill['course_id']}).sort("name",1)

    return render_template('skills.html', course = data_course, skills = documents_all_skills, document = document_skill, save = save)

@app.route('/result/<id>', defaults={'save':0})
@app.route('/result/<id>/<save>')
def result(id, save):
    # obtenemos id del curso
    document_result = mongo.db.resultados.find_one({"_id": ObjectId(id)}, {"course_id":1, "name":1,  
        "correccion":1, "verificabilidad":1, "autenticidad":1, "cognitivo":1, "factual": 1, 
        "conceptual":1, "procedimental": 1, "metacognitivo":1, "estructura":1, "afectivo":1, 
        "tecnologico":1, "colaborativo":1, "observaciones": 1, "revisiones": 1}) 
    data_course = institution(document_result['course_id'])

    documents_all_results = mongo.db.resultados.find({"course_id": document_result['course_id']}).sort("name",1)

    return render_template('results.html', course = data_course, results = documents_all_results, document = document_result, save = save)

@app.route('/instrument/<id>', defaults={'save':0})
@app.route('/instrument/<id>/<save>')
def instrument(id, save):
    # obtenemos id del curso
    documents_instrument = mongo.db.instrumentos.find_one({"_id": ObjectId(id)}, {"course_id":1, "name":1, "correccion": 1, "autenticidad": 1, "observaciones": 1, "revisiones": 1}) 
    data_course = institution(documents_instrument['course_id'])

    documents_all_instruments = mongo.db.instrumentos.find({"course_id": documents_instrument['course_id']}).sort("name",1)

    return render_template('instruments.html', course = data_course, instruments = documents_all_instruments, document = documents_instrument, save = save)

@app.route('/instrument/save/', defaults={'id': 0}, methods=['POST'])
@app.route('/instrument/save/<id>')
def instrument_save(id):
    if request.form['correccion'] != "0": 
        newvalues = { "$set": { "correccion": request.form['correccion'], 
                            "autenticidad": request.form['autenticidad'],
                            "observaciones": request.form['observaciones'] } }
    else:        
        newvalues = { "$set": { "correccion": request.form['correccion']} }

    newrevision = { "$push": 
            { "revisiones": {"usuario": session['username'], "fecha": datetime.now()} }
        }

    # Actualizacion todos instrumentos mismo nombre universidad
    if request.form.get('aplicar'):
        
        # obtenemos universidad a través de id de curso
        document_instrument = mongo.db.instrumentos.find_one({"_id": ObjectId(request.form['id'])}, {"course_id":1, "name":1}) 
        universidad = institution(document_instrument['course_id'])['universidad']        
        area = institution(document_instrument['course_id'])['area']            
        titulo = institution(document_instrument['course_id'])['titulo']

        asignaturas = asignaturas_universidad(universidad, area, titulo)
        lista_asignaturas = []
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))
        
        mongo.db.instrumentos.update_many({
            "name": document_instrument.get('name', ''),
            "course_id": {"$in": lista_asignaturas} 
        }, newrevision)
        
        mongo.db.instrumentos.update_many({
            "name": document_instrument.get('name', ''),
            "course_id": {"$in": lista_asignaturas} 
        }, newvalues)

    # Actualicacion solo instrumento bajo edicion
    else:        
        myquery = { "_id": ObjectId(request.form['id']) }       
        mongo.db.instrumentos.update_one(myquery, newvalues)
        mongo.db.instrumentos.update_one(myquery, newrevision)

    save = 1
    return instrument(request.form['id'], save)

@app.route('/result/save/', defaults={'id': 0}, methods=['POST'])
@app.route('/result/save/<id>')
def result_save(id):
    
    if request.form['correccion'] != "0": 
        newvalues = { "$set":   {   "correccion": request.form['correccion'], 
                                    "verificabilidad": request.form['verificabilidad'],
                                    "autenticidad": request.form['autenticidad'],
                                    "cognitivo": request.form['cognitivo'],
                                    "factual": request.form['factual'],
                                    "conceptual": request.form['conceptual'],
                                    "procedimental": request.form['procedimental'],
                                    "metacognitivo": request.form['metacognitivo'],
                                    "estructura": request.form['estructura'],
                                    "afectivo": request.form['afectivo'],
                                    "tecnologico": request.form['tecnologico'],
                                    "colaborativo": request.form['colaborativo'],
                                    "observaciones": request.form['observaciones'] 
                            }}
    else:
        newvalues = { "$set":   {   "correccion": request.form['correccion'] 
                            }}

    newrevision = { "$push": 
        { "revisiones": {"usuario": session['username'], "fecha": datetime.now()} }
    }

    # Actualizacion todos resultados mismo nombre universidad
    if request.form.get('aplicar'):
        
        # obtenemos universidad a través de id de curso
        document_resultado = mongo.db.resultados.find_one({"_id": ObjectId(request.form['id'])}, {"course_id":1, "name":1}) 
        universidad = institution(document_resultado['course_id'])['universidad']
        area = institution(document_resultado['course_id'])['area']            
        titulo = institution(document_resultado['course_id'])['titulo']
        asignaturas = asignaturas_universidad(universidad, area, titulo)
        lista_asignaturas = []
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))
        
        mongo.db.resultados.update_many({
            "name": document_resultado.get('name', ''),
            "course_id": {"$in": lista_asignaturas} 
        }, newrevision)
        
        mongo.db.resultados.update_many({
            "name": document_resultado.get('name', ''),
            "course_id": {"$in": lista_asignaturas} 
        }, newvalues)

    # Actualicacion solo resultado bajo edicion
    else:
        myquery = { "_id": ObjectId(request.form['id']) }
        mongo.db.resultados.update_one(myquery, newvalues)
        mongo.db.resultados.update_one(myquery, newrevision)

    save = 1
    return result(request.form['id'], save)

@app.route('/skill/save/', defaults={'id': 0}, methods=['POST'])
@app.route('/skill/save/<id>')
def skill_save(id):
    
    if request.form['correccion'] != "0": 
        newvalues = { "$set":   {   "tipo": request.form['tipo'],
                                "correccion": request.form['correccion'], 
                                "cognitivo": request.form['cognitivo'],
                                "factual": request.form['factual'],
                                "conceptual": request.form['conceptual'],
                                "procedimental": request.form['procedimental'],
                                "metacognitivo": request.form['metacognitivo'],
                                "estructura": request.form['estructura'],
                                "afectivo": request.form['afectivo'],
                                "tecnologico": request.form['tecnologico'],
                                "colaborativo": request.form['colaborativo'],
                                "observaciones": request.form['observaciones']
                            }
                 }  
    else:
        newvalues = { "$set":   {   "tipo": request.form['tipo'],
                                "correccion": request.form['correccion'] }}
                                
    newrevision = { "$push": 
        { "revisiones": {"usuario": session['username'], "fecha": datetime.now()} }
    }

    # Actualizacion todas competencias mismo nombre universidad
    if request.form.get('aplicar'):
        
        document_competencia = mongo.db.competencias.find_one({"_id": ObjectId(request.form['id'])}, {"course_id":1, "name":1}) 
            
        # si no es básica, para toda la universidad
        if request.form['tipo'] != '0':
             # obtenemos universidad a través de id de curso
            universidad = institution(document_competencia['course_id'])['universidad']
            area = institution(document_competencia['course_id'])['area']            
            titulo = institution(document_competencia['course_id'])['titulo']
            asignaturas = asignaturas_universidad(universidad, area, titulo)
            lista_asignaturas = []
            for asignatura in asignaturas:
                lista_asignaturas.append(asignatura.get('_id', ''))
            
            mongo.db.competencias.update_many({
                "name": document_competencia.get('name', ''),
                "course_id": {"$in": lista_asignaturas} 
            }, newvalues)
            
            mongo.db.competencias.update_many({
                "name": document_competencia.get('name', ''),
                "course_id": {"$in": lista_asignaturas} 
            }, newrevision)
        # si es básica, para toda la base de datos
        else:            
            mongo.db.competencias.update_many({
                "name": document_competencia.get('name', '') 
            }, newvalues)
            
            mongo.db.competencias.update_many({
                "name": document_competencia.get('name', '')
            }, newrevision)
    # Actualicacion solo competencia bajo edicion
    else:   
        myquery = { "_id": ObjectId(request.form['id']) }
        mongo.db.competencias.update_one(myquery, newvalues)
        mongo.db.competencias.update_one(myquery, newrevision)

    save = 1
    return skill(request.form['id'], save)

def institution(id):
    document_institution = mongo.db.asignaturas.find_one({"_id": id})
    
    data_course = {
        'universidad': document_institution.get('universidad',''),
        'area': document_institution.get('area',''),
        'titulo': document_institution.get('titulo',''),
        'nivel1': document_institution.get('nivel1',''),
        'nivel2': document_institution.get('nivel2',''),
        'asignatura': document_institution.get('asignatura',''),
        'tipo': document_institution.get('tipo',''),
        'creditos': document_institution.get('creditos',''),
        'modalidad': document_institution.get('modalidad',''),
        "_id": document_institution.get('_id','')
        }
    return data_course

def asignaturas_universidad(universidad, area, titulo): 
    if (area == '0' and titulo == '0'):
        documents_asignaturas = mongo.db.asignaturas.find({"universidad": universidad}, {"_id":1}) 
    elif (titulo == '0'):
        documents_asignaturas = mongo.db.asignaturas.find({"universidad": universidad, "area": area}, {"_id":1}) 
    else:
        documents_asignaturas = mongo.db.asignaturas.find({"universidad": universidad, "area": area, "titulo": titulo}, {"_id":1})    
    
    return documents_asignaturas

@app.route('/asignaturas', methods=['POST'])
def asignaturas():
    return 'arreglar'
    
    # asignaturas: necesito universidad, area y titulo. Creo que debería pensar en un formulario dinámico
    # ver vídeo: https://www.youtube.com/watch?v=I2dJuNwlIH0

    # ALTA INSTITUCION
    # 1. Se comprueba si existe
    # 2.    Si no existe, se crea
    
    # ALTA COMPETENCIA
    # 1. Se obtiene id de institución
    # 2. Se comprueba si existe competencia en institución
    # 3.    Si no existe, se crea

@app.route('/cargar_competencias')
def cargar_competencias():
    import csv
    counter = 0
    with open('data/CANCELAR_competencias.csv', newline='') as File:
        reader = csv.reader(File, delimiter=':')
        
        for row in reader:
            counter = counter + 1
            data_course = {
                'universidad': row[0],
                'area': row[1],
                'titulo': row[2],
                'modalidad': row[3],
                'nivel1': row[4],
                'nivel2': row[5],
                'asignatura': row[6],
                'tipo': row[8],
                'creditos': row[7]
                }
            existe_institucion = mongo.db.asignaturas.find_one(data_course)
            if (not(existe_institucion)):
                nuevo = mongo.db.asignaturas.insert_one(data_course)
                id_institucion = nuevo.inserted_id
            else:
                id_institucion = existe_institucion['_id']
            
            data_competencia = {
                'course_id': id_institucion,
                'name': row[9],
                'tipo': tipo_competencia(row[10]),
                'observaciones': row[11]
            }
            existe_competencia = mongo.db.competencias.find_one(data_competencia)
            if(not(existe_competencia)):
                mongo.db.competencias.insert_one(data_competencia)

    print(str(counter))
    return 'COMPETENCIAS CARGADAS!'

@app.route('/cargar_resultados')
def cargar_resultados():
    import csv
    counter = 0
    # ficher errores
    ferrores = open("errores_results.log","w")
    with open('data/CANCELAR_resultados.csv', newline='') as File:
        reader = csv.reader(File, delimiter=':')
        
        for row in reader:
            counter = counter + 1
            
            data_course = {
                'universidad': row[0],
                'area': row[1],
                'titulo': row[2],
                'modalidad': row[3],
                'nivel1': row[4],
                'nivel2': row[5],
                'asignatura': row[6],
                'creditos': row[7],
                'tipo': row[8]                
                }
            existe_asignatura = mongo.db.asignaturas.find_one(data_course)
            if (not(existe_asignatura)):
                #nuevo = mongo.db.asignaturas.insert_one(data_course)
                #id_asignatura = nuevo.inserted_id
                id_asignatura = 0
                print("Linea: " + str(counter) + " no existe asignatura")
                # ferrores.write("Linea:"+str(counter))
                ferrores.write(str(data_course))
                ferrores.write("-------------")
            else:
                id_asignatura = existe_asignatura['_id']
            
            data_resultado = {
                'course_id': id_asignatura,
                'name': row[9],
                'observaciones': row[10]
            }
            
            # REVISAR UPV RESULTADOS ...
            # print(counter)
            if (data_resultado['name'] != "NO APARECE" and data_resultado['name'] != ""):
                #print(str(counter) + " no existe resultado")
                existe_resultado = mongo.db.resultados.find_one(data_resultado)
                if(not(existe_resultado)):
                    mongo.db.resultados.insert_one(data_resultado)

    print(counter)
    return 'RESULTADOS CARGADOS!'

@app.route('/cargar_instrumentos')
def cargar_instrumentos():
    import csv
    counter = 0
    with open('data/ucor_medios.csv', newline='') as File:
        reader = csv.reader(File, delimiter=':')
        
        ferrores = open("errores_medios.log","w")
        for row in reader:
            counter = counter + 1
            
            data_course = {
                'universidad': row[0],
                'area': row[1],
                'titulo': row[2],
                'modalidad': row[3],
                'nivel1': row[4],
                'nivel2': row[5],
                'asignatura': row[6],
                'creditos': row[7],
                'tipo': row[8]                
                }
            existe_asignatura = mongo.db.asignaturas.find_one(data_course)
            
            if (not(existe_asignatura)):
                # nuevo = mongo.db.asignaturas.insert_one(data_course)
                # id_asignatura = nuevo.inserted_id
                id_asignatura = 0
                print("Linea: " + str(counter) + " no existe asignatura")
                ferrores.write(str(data_course))
                print("------------------")
            else:
                id_asignatura = existe_asignatura['_id']
            
            data_instrumento = {
                'course_id': id_asignatura,
                'name': row[9],
                'observaciones': row[10]
            }
            
            #print(counter)
            if (data_instrumento['name'] != "No existe" and data_instrumento['name'] != ""):
                #print(str(counter) + " no existe resultado")
                existe_instrumento = mongo.db.instrumentos.find_one(data_instrumento)
                if(not(existe_instrumento)):
                    mongo.db.instrumentos.insert_one(data_instrumento)

    return 'INSTRUMENTOS CARGADOS!'

# ---------------------------------------------------------------------------------------------
# Informes_general: diagrama de barras con los datos de componentes registrados por universidad
# ---------------------------------------------------------------------------------------------

@app.route('/informes_general')
@app.route('/informes_general', methods=['POST'])
def informes_general():
    if 'username' not in session:
        return login(0)

    # Consultas comprobacion datos insertados
    # correccion -1 son aquellos entes cuya correccion no se ha definido entre los valores esperados
    # por tanto, se consideran no valoradas aunque existan otros campos
    query_competencias = { '$and': [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}] }
    query_medios = { '$and': [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}] }
    query_resultados = { '$and': [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}] }
    query = {}

    if 'universidad' in session:
        universidad = session['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad", {"universidad": universidad})
    elif request.form.get('universidad'):
        universidad = request.form['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad")
    else:
        universidad = 'TODAS'
        documents_unis = mongo.db.asignaturas.distinct("universidad")

    lista_asignaturas = []
    if universidad != 'TODAS':
        asignaturas = asignaturas_universidad(universidad,'0','0')        
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))
        query = {'course_id':{'$in': lista_asignaturas}}
        
        query_competencias['course_id'] = query['course_id']
        query_medios['course_id'] = query['course_id']
        query_resultados['course_id'] = query['course_id']
    

    data = {
        'competencias': {
            'registradas': mongo.db.competencias.count_documents(query_competencias),
            'total': mongo.db.competencias.count_documents(query)
        },
        'medios': {
            'registradas': mongo.db.instrumentos.count_documents(query_medios),
            'total': mongo.db.instrumentos.count_documents(query)
        },
        'resultados': {
            'registradas': mongo.db.resultados.count_documents(query_resultados),
            'total': mongo.db.resultados.count_documents(query)
        }
    } 

    data['competencias']['pendientes'] = int(data['competencias']['total']) - int(data['competencias']['registradas'])
    data['medios']['pendientes'] = int(data['medios']['total']) - int(data['medios']['registradas'])
    data['resultados']['pendientes'] = int(data['resultados']['total']) - int(data['resultados']['registradas'])
    data['universidad'] = universidad 
   
    return render_template('report.html', universidades = documents_unis, selected = {'universidad': universidad}, data = data)

# ---------------------------------------------------------------------------------------------
# Informes_combinados: selecciona dos elementos y muestra los diagramas de tartas para ambos
# ---------------------------------------------------------------------------------------------

@app.route('/informes_combinados')
@app.route('/informes_combinados', methods=['POST'])
def informes_combinados():
    if 'username' not in session:
        return login(0)            

    if request.form.get('university'):
        data_selected = {
            'universidad': request.form.get('university',''),
            'area': request.form.get('area','0'),
            'titulo': request.form.get('titulo','0'),
            'universidadCompara': request.form.get('universityCompara',''),
            'areaCompara': request.form.get('areaCompara',''),
            'tituloCompara': request.form.get('tituloCompara',''),
            'tipoCompetencia': request.form.get('tipoCompetencia'),
            'componente': request.form.get('componente')
            } 
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        documents_area = mongo.db.asignaturas.distinct("area", {"universidad": data_selected["universidad"]}) 
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": data_selected["universidad"], "area": data_selected["area"]}) 
        documents_area_compara = mongo.db.asignaturas.distinct("area", {"universidad": data_selected["universidadCompara"]}) 
        documents_titu_compara = mongo.db.asignaturas.distinct("titulo", {"universidad": data_selected["universidadCompara"], "area": data_selected["areaCompara"]}) 

        buscar_registrados =   [{'correccion':{'$exists': True}}, 
                                {'correccion': {'$ne': '-1'}}]
        buscar_correctos =   [{'correccion':{'$exists': True}}, 
                                {'correccion': {'$ne': '-1'}}, 
                                {'correccion': {'$ne': '0'}}]
        if 'tipoCompetencia' in data_selected:
            if data_selected['tipoCompetencia'] != '4': # Si no es TODAS
                buscar_registrados.append({'tipo': data_selected["tipoCompetencia"]})
                buscar_correctos.append({'tipo': data_selected["tipoCompetencia"]})

        buscar1_registrados = buscar_registrados.copy()
        buscar1_correctos = buscar_correctos.copy()
        
        asignaturas = asignaturas_universidad(data_selected["universidad"],data_selected["area"],data_selected["titulo"]) 
        lista_asignaturas = []       
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))

        buscar1_registrados.append({"course_id": { "$in": lista_asignaturas}})
        query_registrados = { '$and': buscar1_registrados }  
        
        buscar1_correctos.append({"course_id": { "$in": lista_asignaturas}})
        query_correctos = { '$and': buscar1_correctos }  
        
        lista_asignaturas_compara = []

        asignaturas_compara = asignaturas_universidad(data_selected["universidadCompara"],data_selected["areaCompara"],data_selected["tituloCompara"])        
        for asignatura in asignaturas_compara:
            lista_asignaturas_compara.append(asignatura.get('_id', ''))
        

        buscar2_registrados =  buscar_registrados.copy()
        buscar2_registrados.append({"course_id": { "$in": lista_asignaturas_compara}})
        
        buscar2_correctos =  buscar_correctos.copy()
        buscar2_correctos.append({"course_id": { "$in": lista_asignaturas_compara}})

        query_compara_registrados = { '$and': buscar2_registrados }
        query_compara_correctos = { '$and': buscar2_correctos }

        if data_selected['componente'] == 'competencias':        
            data = {
                'items': {
                    'registradas': mongo.db[data_selected['componente']].count_documents(query_registrados),
                    'correctos': mongo.db[data_selected['componente']].count_documents(query_correctos),
                    'correccion': report_correccion(data_selected['componente'],buscar1_registrados),
                    'cognitivo': report_cognitivo(data_selected['componente'], buscar1_correctos),
                    'estructura': report_estructura(data_selected['componente'], buscar1_correctos),
                    'afectivo': report_afectivo(data_selected['componente'], buscar1_correctos),
                    'tecnologico': report_tecnologico(data_selected['componente'], buscar1_correctos),
                    'colaborativo': report_colaborativo(data_selected['componente'], buscar1_correctos),
                    'factual': report_factual(data_selected['componente'], buscar1_correctos),
                    'metacognitivo': report_metacognitivo(data_selected['componente'], buscar1_correctos),
                    'procedimental': report_procedimental(data_selected['componente'], buscar1_correctos),
                    'conceptual': report_conceptual(data_selected['componente'], buscar1_correctos)
                },
                'items_compara': {
                    'registradas': mongo.db[data_selected['componente']].count_documents(query_compara_registrados),
                    'correctos': mongo.db[data_selected['componente']].count_documents(query_compara_correctos),
                    'correccion': report_correccion(data_selected['componente'],buscar2_registrados),
                    'cognitivo': report_cognitivo(data_selected['componente'], buscar2_correctos),
                    'estructura': report_estructura(data_selected['componente'], buscar2_correctos),
                    'afectivo': report_afectivo(data_selected['componente'], buscar2_correctos),
                    'tecnologico': report_tecnologico(data_selected['componente'], buscar2_correctos),
                    'colaborativo': report_colaborativo(data_selected['componente'], buscar2_correctos),
                    'factual': report_factual(data_selected['componente'], buscar2_correctos),
                    'metacognitivo': report_metacognitivo(data_selected['componente'], buscar2_correctos),
                    'procedimental': report_procedimental(data_selected['componente'], buscar2_correctos),
                    'conceptual': report_conceptual(data_selected['componente'], buscar2_correctos)
                }
            }
         
        elif data_selected['componente'] == 'resultados':        
            data = {
                'items': {
                    'registradas': mongo.db[data_selected['componente']].count_documents(query_registrados),
                    'correctos': mongo.db[data_selected['componente']].count_documents(query_correctos),
                    'correccion': report_correccion(data_selected['componente'],buscar1_registrados),
                    'cognitivo': report_cognitivo(data_selected['componente'], buscar1_correctos),
                    'estructura': report_estructura(data_selected['componente'], buscar1_correctos),
                    'afectivo': report_afectivo(data_selected['componente'], buscar1_correctos),
                    'tecnologico': report_tecnologico(data_selected['componente'], buscar1_correctos),
                    'colaborativo': report_colaborativo(data_selected['componente'], buscar1_correctos),
                    'factual': report_factual(data_selected['componente'], buscar1_correctos),
                    'metacognitivo': report_metacognitivo(data_selected['componente'], buscar1_correctos),
                    'procedimental': report_procedimental(data_selected['componente'], buscar1_correctos),
                    'conceptual': report_conceptual(data_selected['componente'], buscar1_correctos),
                    'autenticidad': report_autenticidad(data_selected['componente'],buscar1_correctos)
                },
                'items_compara': {
                    'registradas': mongo.db[data_selected['componente']].count_documents(query_compara_registrados),
                    'correctos': mongo.db[data_selected['componente']].count_documents(query_compara_correctos),
                    'correccion': report_correccion(data_selected['componente'],buscar2_registrados),
                    'cognitivo': report_cognitivo(data_selected['componente'], buscar2_correctos),
                    'estructura': report_estructura(data_selected['componente'], buscar2_correctos),
                    'afectivo': report_afectivo(data_selected['componente'], buscar2_correctos),
                    'tecnologico': report_tecnologico(data_selected['componente'], buscar2_correctos),
                    'colaborativo': report_colaborativo(data_selected['componente'], buscar2_correctos),
                    'factual': report_factual(data_selected['componente'], buscar2_correctos),
                    'metacognitivo': report_metacognitivo(data_selected['componente'], buscar2_correctos),
                    'procedimental': report_procedimental(data_selected['componente'], buscar2_correctos),
                    'conceptual': report_conceptual(data_selected['componente'], buscar2_correctos),
                    'autenticidad': report_autenticidad(data_selected['componente'],buscar2_correctos)
                }
            }

        else:
                
            data = {
                'items': {
                    'registradas': mongo.db[data_selected['componente']].count_documents(query_registrados),
                    'correctos': mongo.db[data_selected['componente']].count_documents(query_correctos),
                    'correccion': report_correccion(data_selected['componente'],buscar1_registrados),
                    'autenticidad': report_autenticidad(data_selected['componente'],buscar1_correctos)
                },
                'items_compara': {
                    'registradas': mongo.db[data_selected['componente']].count_documents(query_compara_registrados),
                    'correctos': mongo.db[data_selected['componente']].count_documents(query_compara_correctos),
                    'correccion': report_correccion(data_selected['componente'],buscar2_registrados),
                    'autenticidad': report_autenticidad(data_selected['componente'],buscar2_correctos)
                }
            } 

    else:
        data_selected = { 'componente': 'competencias' }
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        documents_area = {}
        documents_titu = {}
        documents_area_compara = {}
        documents_titu_compara = {}
        data = {}

    return render_template('report_combinacion.html', universidades = documents_unis, areas = documents_area, 
    titulos = documents_titu, areasCompara = documents_area_compara, titulosCompara = documents_titu_compara,  selected = data_selected, 
    data = data)

# ---------------------------------------------------------------------------------------------
# Informes_competencias: diagrama de porciones de tartas de competencias por universidad
# ---------------------------------------------------------------------------------------------

@app.route('/informes_competencias')
@app.route('/informes_competencias', methods=['POST'])
def informes_competencias():
    if 'username' not in session:
        return login(0)
    
    # Consultas comprobacion datos insertados
    # correccion -1 son aquellos entes cuya correccion no se ha definido entre los valores esperados
    # por tanto, se consideran no valoradas aunque existan otros campos
    buscar_registradas =   [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}]
    query_competencias_registradas = { '$and': buscar_registradas }
    query = {}
    
    buscar_correctas =   [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}, {'correccion': {'$ne': '0'}}]
    query_competencias_correctas = { '$and': buscar_correctas }

    if 'universidad' in session:
        universidad = session['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad", {"universidad": universidad})
    elif request.form.get('universidad'):
        universidad = request.form['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad")
    else:
        universidad = 'TODAS'
        documents_unis = mongo.db.asignaturas.distinct("universidad")

    
    lista_asignaturas = []
    if universidad != 'TODAS':
        asignaturas = asignaturas_universidad(universidad,'0','0')        
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))
        query = {'course_id':{'$in': lista_asignaturas}}
        buscar_registradas.append({"course_id": { "$in": lista_asignaturas}})
        buscar_correctas.append({"course_id": { "$in": lista_asignaturas}})
        
        query_competencias_registradas['course_id'] = query['course_id']
        query_competencias_correctas['course_id'] = query['course_id']
    

    data = {
        'competencias': {
            'registradas': mongo.db.competencias.count_documents(query_competencias_registradas),
            'total': mongo.db.competencias.count_documents(query),
            'correctas': mongo.db.competencias.count_documents(query_competencias_correctas),
            'correccion': report_correccion("competencias", buscar_registradas),
            'cognitivo': report_cognitivo("competencias", buscar_correctas),
            'estructura': report_estructura("competencias", buscar_correctas),
            'afectivo': report_afectivo("competencias", buscar_correctas),
            'tecnologico': report_tecnologico("competencias", buscar_correctas),
            'colaborativo': report_colaborativo("competencias", buscar_correctas),
            'factual': report_factual("competencias", buscar_correctas),
            'metacognitivo': report_metacognitivo("competencias", buscar_correctas),
            'procedimental': report_procedimental("competencias", buscar_correctas),
            'conceptual': report_conceptual("competencias", buscar_correctas)
        }
    } 

    data['competencias']['pendientes'] = int(data['competencias']['total']) - int(data['competencias']['registradas'])
    data['universidad'] = universidad 
   
    return render_template('report_competencias.html', universidades = documents_unis, selected = {'universidad': universidad}, data = data)

# ---------------------------------------------------------------------------------------------
# Informes_resultados: diagrama de porciones de tartas de resultados por universidad
# ---------------------------------------------------------------------------------------------

@app.route('/informes_resultados')
@app.route('/informes_resultados', methods=['POST'])
def informes_resultados():
    if 'username' not in session:
        return login(0)

    # Consultas comprobacion datos insertados
    # correccion -1 son aquellos entes cuya correccion no se ha definido entre los valores esperados
    # por tanto, se consideran no valoradas aunque existan otros campos
    buscar_registradas =   [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}]
    query_resultados_registradas= { '$and': buscar_registradas }
    query = {}
    
    buscar_correctos =   [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}, {'correccion': {'$ne': '0'}}]
    query_resultados_correctos = { '$and': buscar_correctos }

    if 'universidad' in session:
        universidad = session['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad", {"universidad": universidad})
    elif request.form.get('universidad'):
        universidad = request.form['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad")
    else:
        universidad = 'TODAS'
        documents_unis = mongo.db.asignaturas.distinct("universidad")

    lista_asignaturas = []
    if universidad != 'TODAS':
        asignaturas = asignaturas_universidad(universidad,'0','0')        
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))
        query = {'course_id':{'$in': lista_asignaturas}}
        buscar_registradas.append({"course_id": { "$in": lista_asignaturas}})
        buscar_correctos.append({"course_id": { "$in": lista_asignaturas}})
        
        query_resultados_registradas['course_id'] = query['course_id']
        query_resultados_correctos['course_id'] = query['course_id']
    

    data = {
        'resultados': {
            'registrados': mongo.db.resultados.count_documents(query_resultados_registradas),
            'total': mongo.db.resultados.count_documents(query),
            'correctos': mongo.db.resultados.count_documents(query_resultados_correctos),
            'correccion': report_correccion("resultados", buscar_registradas),
            'cognitivo': report_cognitivo("resultados", buscar_correctos),
            'estructura': report_estructura("resultados", buscar_correctos),
            'afectivo': report_afectivo("resultados", buscar_correctos),
            'tecnologico': report_tecnologico("resultados", buscar_correctos),
            'colaborativo': report_colaborativo("resultados", buscar_correctos),
            'verificabilidad': report_verificabilidad("resultados", buscar_correctos),
            'autenticidad': report_autenticidad("resultados", buscar_correctos),
            'factual': report_factual("resultados", buscar_correctos),
            'metacognitivo': report_metacognitivo("resultados", buscar_correctos),
            'procedimental': report_procedimental("resultados", buscar_correctos),
            'conceptual': report_conceptual("resultados", buscar_correctos)
        }
    } 

    data['resultados']['pendientes'] = int(data['resultados']['total']) - int(data['resultados']['registrados'])
    data['universidad'] = universidad 
   
    return render_template('report_resultados.html', universidades = documents_unis, selected = {'universidad': universidad}, data = data)

# ---------------------------------------------------------------------------------------------
# Informes_medios: diagrama de porciones de tartas de medios de evaluación por universidad
# Nota:     en la BD los medios se almacenan en la colección 'instrumentos', pero en la 
#           nomenclatura del proyecto se denominan medios de evaluación.
# ---------------------------------------------------------------------------------------------
@app.route('/informes_medios')
@app.route('/informes_medios', methods=['POST'])
def informes_medios():
    if 'username' not in session:
        return login(0)

    # Consultas comprobacion datos insertados
    # correccion -1 son aquellos entes cuya correccion no se ha definido entre los valores esperados
    # por tanto, se consideran no valoradas aunque existan otros campos
    buscar_registrados=   [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}]
    query_medios_registrados= { '$and': buscar_registrados}
    query = {}
    buscar_correctos=   [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}, {'correccion': {'$ne': '0'}}]
    query_medios_correctos= { '$and': buscar_correctos}

    if 'universidad' in session:
        universidad = session['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad", {"universidad": universidad})
    elif request.form.get('universidad'):
        universidad = request.form['universidad']
        documents_unis = mongo.db.asignaturas.distinct("universidad")
    else:
        universidad = 'TODAS'
        documents_unis = mongo.db.asignaturas.distinct("universidad")

    lista_asignaturas = []
    if universidad != 'TODAS':
        asignaturas = asignaturas_universidad(universidad,'0','0')        
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))
        query = {'course_id':{'$in': lista_asignaturas}}
        buscar_registrados.append({"course_id": { "$in": lista_asignaturas}})
        buscar_correctos.append({"course_id": { "$in": lista_asignaturas}})
        
        query_medios_registrados['course_id'] = query['course_id']
        query_medios_correctos['course_id'] = query['course_id']

    data = {
        'medios': {
            'registrados': mongo.db.instrumentos.count_documents(query_medios_registrados),
            'total': mongo.db.instrumentos.count_documents(query),
            'correctos': mongo.db.instrumentos.count_documents(query_medios_correctos),
            'correccion': report_correccion("instrumentos", buscar_registrados),
            'autenticidad': report_autenticidad("instrumentos", buscar_correctos)
        }
    } 

    data['medios']['pendientes'] = int(data['medios']['total']) - int(data['medios']['registrados'])
    data['universidad'] = universidad 
   
    return render_template('report_medios.html', universidades = documents_unis, selected = {'universidad': universidad}, data = data)

# ---------------------------------------------------------------------------------------------
# report_xxxxxx: datos de las categorías de competencias, resultados y medios
#   Hay una función para cada uno de ellos. Devuelve un array asociativo con el número de
#   elementos que hay para cada valor dentro de la categoría
# ---------------------------------------------------------------------------------------------

def report_procedimental(element, query): 
    query1 = query.copy()
    query1.append({"procedimental": { "$exists":"true"}})    
      
    pipeline = build_pipeline(query1, "$procedimental")

    data = mongo.db[element].aggregate(pipeline)

    lista_procedimental = {0:0, 1:0, 2:0}
    for tipo in data:
            lista_procedimental[int(tipo.get('_id', ''))] = tipo.get('count', '')

    return lista_procedimental

def report_metacognitivo(element, query): 
    query1 = query.copy()
    query1.append({"metacognitivo": { "$exists":"true"}})    
      
    pipeline = build_pipeline(query1, "$metacognitivo")

    data = mongo.db[element].aggregate(pipeline)

    lista_metacognitivo = {0:0, 1:0, 2:0}
    for tipo in data:
            lista_metacognitivo[int(tipo.get('_id', ''))] = tipo.get('count', '')

    return lista_metacognitivo

def report_conceptual(element, query): 
    query1 = query.copy()
    query1.append({"conceptual": { "$exists":"true"}})    
      
    pipeline = build_pipeline(query1, "$conceptual")

    data = mongo.db[element].aggregate(pipeline)

    lista_conceptual = {0:0, 1:0, 2:0}
    for tipo in data:
            lista_conceptual[int(tipo.get('_id', ''))] = tipo.get('count', '')

    return lista_conceptual

def report_factual(element, query): 
    query1 = query.copy()
    query1.append({"factual": { "$exists":"true"}})    
      
    pipeline = build_pipeline(query1, "$factual")

    data = mongo.db[element].aggregate(pipeline)

    lista_factual = {0:0, 1:0, 2:0}
    for tipo in data:
            lista_factual[int(tipo.get('_id', ''))] = tipo.get('count', '')

    return lista_factual

def report_afectivo(element, query):  
    query1 = query.copy()
    query1.append({"afectivo": { "$exists":"true"}})    
      
    pipeline = build_pipeline(query1, "$afectivo")

    data = mongo.db[element].aggregate(pipeline)

    lista_afectivo = {0:0, 1:0}
    for tipo in data:
            lista_afectivo[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_afectivo

def report_tecnologico(element, query):  
    query1 = query.copy()
    query1.append({"tecnologico": { "$exists":"true"}})     

    pipeline = build_pipeline(query1, "$tecnologico")

    data = mongo.db[element].aggregate(pipeline)

    lista_tecnologico = {0:0, 1:0}
    for tipo in data:
            lista_tecnologico[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_tecnologico

def report_colaborativo(element, query):
    query1 = query.copy()
    query1.append({"colaborativo": { "$exists":"true"}})  
      
    pipeline = build_pipeline(query1, "$colaborativo")

    data = mongo.db[element].aggregate(pipeline)

    lista_colaborativo = {0:0, 1:0}
    for tipo in data:
            lista_colaborativo[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_colaborativo

def report_cognitivo(element, query):
    query1 = query.copy()
    query1.append({"cognitivo": { "$exists":"true"}}) 

    pipeline = build_pipeline(query1, "$cognitivo")

    data = mongo.db[element].aggregate(pipeline)

    lista_cognitivo = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    
    for tipo in data:
        lista_cognitivo[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_cognitivo

def report_correccion(element,query):    
    pipeline = build_pipeline(query, "$correccion")

    data = mongo.db[element].aggregate(pipeline)

    # Tipos de corrección
    lista_correccion = { -1: 0, 0: 0, 1: 0, 2: 0 }

    for tipo in data:
        lista_correccion[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_correccion

def report_autenticidad(element,query):    
    query1 = query.copy()
    query1.append({"autenticidad": {"$exists": "true"}})

    pipeline = build_pipeline(query1, "$autenticidad")

    data = mongo.db[element].aggregate(pipeline)

    # Tipos de autenticidad
    lista_autenticidad = { -1: 0, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }

    for tipo in data:
        lista_autenticidad[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_autenticidad

def report_verificabilidad(element,query):    
    query1 = query.copy()
    query1.append({"verificabilidad": {"$exists": "true"}})

    pipeline = build_pipeline(query1, "$verificabilidad")

    data = mongo.db[element].aggregate(pipeline)

    # Tipos de verificabilidad
    lista_verificabilidad = { -1: 0, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }

    for tipo in data:
        lista_verificabilidad[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_verificabilidad

def report_estructura(element, query):
    query1 = query.copy()
    query1.append({"estructura": { "$exists":"true"}}) 
    
    pipeline = build_pipeline(query1, "$estructura")

    data = mongo.db[element].aggregate(pipeline)

    lista_estructura = {1:0, 2:0, 3:0, 4:0, 5:0}
    for tipo in data:
            lista_estructura[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_estructura

# ---------------------------------------------------------------------------------------------
# Build_pipeline: Crea un pipeline para la consulta mongo. Lo utilizan los reports para generar las consultas
# Nota:     Recibe el filtrado y el elemento que se utilizará como id para el group by
# ---------------------------------------------------------------------------------------------
 
def build_pipeline(filter, element_grouped):

    pipeline = [
                {
                    "$match":
                    {
                        "$and": filter
                    }
                },
                {
                    "$group": 
                    {
                        "_id": element_grouped,
                        "count": { "$sum": 1}
                    }
                },
                {
                    "$sort":
                    {
                        "_id": 1
                    }
                }
            ]
    return pipeline

def tipo_competencia(tipo):
    switcher = {
        "Básicas": '0',
        "Específicas": '1',
        "Generales": '2',
        "Transversales": '3'
    }
    return switcher.get(tipo, "Invalid option")

def tipo_asignatura(tipo):
    switcher = {
        "Básicas": '0',
        "Específicas": '1',
        "Generales": '2',
        "Transversales": '3'
    }
    return switcher.get(tipo, "Invalid option")

# ---------------------------------------------------------------------------------------------
# Pendientes: Listado con componentes pendientes de ser valorados
# ---------------------------------------------------------------------------------------------

@app.route('/pendientes', defaults={'universidad': 0})
@app.route('/pendientes/<universidad>')
def pendientes(universidad):
    documents_skills={}
    documents_results={}
    documents_instruments={}

    # Si hay universidad se muestra, sino en blanco
    if universidad!=0:
        documents_asignaturas = mongo.db.asignaturas.find({"universidad": universidad}, {"_id":1}) 

        lista_asignaturas = []
        for asignatura in documents_asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))

             
        # skills
        documents_skills = mongo.db.competencias.find({'$and':[{'$or':[{'correccion':{'$exists': False}}, {'correccion': {'$eq': '-1'}}]}, {"course_id": {'$in':lista_asignaturas}}]}).sort("name",1)
        documents_results = mongo.db.resultados.find({'$and':[{'$or':[{'correccion':{'$exists': False}}, {'correccion': {'$eq': '-1'}}]}, {"course_id": {'$in':lista_asignaturas}}]}).sort("name",1)
        documents_instruments = mongo.db.instrumentos.find({'$and':[{'$or':[{'correccion':{'$exists': False}}, {'correccion': {'$eq': '-1'}}]}, {"course_id": {'$in':lista_asignaturas}}]}).sort("name",1)

    return render_template('pendientes.html', skills = documents_skills, results = documents_results, instruments = documents_instruments)

# -----------------------
# Es necesario eliminar un título de Oviedo. 
# Creamos rutina para ello
# -----------------------

@app.route('/eliminar_titulo')
def eliminar_titulo():
    universidad = "Universidad de Oviedo"
    area = "Economía y Empresa"
    titulo = "Máster Universitario en Estudios de Economía Sectorial"

    universidad_enc = universidad.encode('latin1')
    area_enc = area.encode('latin1')
    titulo_enc = titulo.encode('latin1')

    asignaturas = asignaturas_universidad(universidad_enc.decode('utf-8'), area_enc.decode('utf-8'), titulo_enc.decode('utf-8')) 
    lista_asignaturas = []       
    for asignatura in asignaturas:
        print("Asignatura: ")
        print(asignatura['_id'])
        query = {'course_id': ObjectId(asignatura['_id'])}
        mongo.db.competencias.delete_many(query)
        print("Competencias borradas")
        mongo.db.resultados.delete_many(query)
        print("Resultados borrados")
        mongo.db.instrumentos.delete_many(query)
        print("Instrumentos borrados")

    return "Borrado de titulo indicado realizado."



# Función para recomendar resultados 
@app.route('/recomendador_resultados/')
@app.route('/recomendador_resultados/', methods=['POST'])
def recomendador_resultados():
    document_rec = {
        'name': 'Sugerencia de detalles para el resultado descrito',
        'prob': 0.0
    }

    if request.method == 'POST':
        sugerencias_rec = sugerir_resultado(request.form['descripcion'])
        descripcion_proporcionada_rec = request.form['descripcion']
        document_rec = mongo.db.resultados.find_one({"_id": ObjectId(sugerencias_rec[0][0])})
        
    else:        
        descripcion_proporcionada_rec = "--- Describa en este espacio el resultado ---"
        sugerencias_rec = {}
    
    return render_template('recommender_results.html', document = document_rec, sugerencias = sugerencias_rec, descripcion_proporcionada = descripcion_proporcionada_rec)

def sugerir_resultado(result):

    elements = 10
    resultados = mongo.db.resultados.find()
    sugerencia = [(0, 0.0, "vacio")]*elements
# por aqui
    for resultado in resultados:
        prob = similar(resultado['name'],result)
        if prob > sugerencia[elements-1][1]:
            sugerencia[elements-1] = (resultado['_id'], prob, resultado['name'])            

            i = elements-1
            while i > 0 and prob > sugerencia[i-1][1]:
                sugerencia[i] = sugerencia[i-1]
                i = i-1
            
            sugerencia[i] = (resultado['_id'], prob, resultado['name']) 
    
    
    return sugerencia

# Función para recomendar competencias
@app.route('/recomendador_competencias/')
@app.route('/recomendador_competencias/', methods=['POST'])
def recomendador_competencias():
    document_rec = {
        'name': 'Sugerencia de detalles para la competencia descrita',
        'prob': 0.0
    }

    if request.method == 'POST':
        sugerencias_rec = sugerir_competencia(request.form['descripcion'])
        descripcion_proporcionada_rec = request.form['descripcion']
        document_rec = mongo.db.competencias.find_one({"_id": ObjectId(sugerencias_rec[0][0])})
        
    else:        
        descripcion_proporcionada_rec = "--- Describa en este espacio la competencia ---"
        sugerencias_rec = {}
    
    return render_template('recommender_skills.html', document = document_rec, sugerencias = sugerencias_rec, descripcion_proporcionada = descripcion_proporcionada_rec)

def sugerir_competencia(skill):

    elements = 10
    competencias = mongo.db.competencias.find()
    sugerencia = [(0, 0.0, "vacio")]*elements

    for competencia in competencias:
        prob = similar(competencia['name'],skill)
        if prob > sugerencia[elements-1][1]:
            sugerencia[elements-1] = (competencia['_id'], prob, competencia['name'])            

            i = elements-1
            while i > 0 and prob > sugerencia[i-1][1]:
                sugerencia[i] = sugerencia[i-1]
                i = i-1
            
            sugerencia[i] = (competencia['_id'], prob, competencia['name']) 
    
    
    return sugerencia

@app.route('/copiar_resultados_similares')
def copiar_resultados_similares():
    resultados_test = list(mongo.db.resultados_test1.find())
    resultados_training = list(mongo.db.resultados_training.find())
    contador = 0

    for doc_test in resultados_test:
        max_similitud = 0.0
        documento_similar = None

        for doc_training in resultados_training:
            similitud = similar(doc_test['name'], doc_training['name'])
            if similitud > max_similitud:
                max_similitud = similitud
                documento_similar = doc_training

        if documento_similar:
            # Copiar valores del documento similar a resultados-test
            if documento_similar['correccion'] == "0":
                doc_test['correccion'] = documento_similar['correccion']
            else:
                # Si la corrección es diferente de "0", copiar todos los campos relevantes
                campos_a_copiar = ['afectivo', 'autenticidad', 'cognitivo', 'colaborativo', 'conceptual',
                                   'estructura', 'factual', 'metacognitivo', 'procedimental', 'tecnologico',
                                   'verificabilidad', 'correccion']
                for campo in campos_a_copiar:
                    doc_test[campo] = documento_similar[campo]

            # Actualizar el documento en la colección resultados-test
            mongo.db.resultados_test1.update_one({'_id': doc_test['_id']}, {'$set': doc_test})
            contador += 1
            print("Procesando documento ", contador)

    return "the end"


@app.route('/sugerir_similares/<coleccion_principal>')
def sugerir_similares(coleccion_principal):
    if coleccion_principal not in ['resultados', 'competencias']:
        return "Error: La colección principal no es válida"

    # Construir los nombres de las colecciones
    coleccion_test_name = f"{coleccion_principal}_test1"
    coleccion_training_name = f"{coleccion_principal}_training"

    # Obtener documentos de las colecciones
    documentos_test = list(mongo.db[coleccion_test_name].find())
    documentos_training = list(mongo.db[coleccion_training_name].find())

    contador = 0

    for doc_test in documentos_test:
        max_similitud = 0.0
        documento_similar = None

        for doc_training in documentos_training:
            similitud = similar(doc_test['name'], doc_training['name'])
            if similitud > max_similitud:
                max_similitud = similitud
                documento_similar = doc_training

        if documento_similar:
            # Copiar valores del documento similar a resultados-test
            if documento_similar['correccion'] == "0":
                doc_test['correccion'] = documento_similar['correccion']
            else:
                # Si la corrección es diferente de "0", copiar todos los campos relevantes
                campos_a_copiar = ['afectivo', 'cognitivo', 'colaborativo', 'conceptual',
                               'estructura', 'factual', 'metacognitivo', 'procedimental',
                               'tecnologico', 'correccion']

                # Copiar campos relevantes
                for campo in campos_a_copiar:
                    doc_test[campo] = documento_similar[campo]

            # Actualizar el documento en la colección de test
            mongo.db[coleccion_test_name].update_one({'_id': doc_test['_id']}, {'$set': doc_test})
            contador += 1
            print(f"Procesando documento {contador} en la colección {coleccion_test_name}")

    return "the end"


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

import os
	
if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug = True)
    #app.run(port = 3000, debug = True)
