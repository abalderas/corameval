#!/usr/bin/python
# -*- coding: latin-1 -*-
from flask import Flask, render_template, url_for, request, jsonify, json, session
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from flask_bcrypt import bcrypt
from datetime import datetime

# librerías para la figura
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt; plt.rcdefaults()
#import numpy as np
#import matplotlib.pyplot as plt

app = Flask(__name__)

# Database connection
app.config.from_json('config/config.json')
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

# STATUS:
#
# Muestra comparación de competencias entre títulos (hay que seleccionar los 3 niveles)
#       --> Mejora 1: realizar comparación desde un solo nivel
#       --> Mejora 2: ampliar a resultados y medios
#       --> Mejora 3: cambiar formato de tartas (¿quitar leyendas, cambiar de sitio, ...? estudiar)
#
# Llevar a koala y probar

@app.route('/informes_combinados')
@app.route('/informes_combinados', methods=['POST'])
def informes_combinados():
    if 'username' not in session:
        return login(0)       
       

    if request.form.get('university'):
        data_selected = {
            'universidad': request.form.get('university',''),
            'area': request.form.get('area',''),
            'titulo': request.form.get('titulo',''),
            'universidadCompara': request.form.get('universityCompara',''),
            'areaCompara': request.form.get('areaCompara',''),
            'tituloCompara': request.form.get('tituloCompara',''),
            } 
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        documents_area = mongo.db.asignaturas.distinct("area", {"universidad": data_selected["universidad"]}) 
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": data_selected["universidad"], "area": data_selected["area"]}) 
        documents_area_compara = mongo.db.asignaturas.distinct("area", {"universidad": data_selected["universidadCompara"]}) 
        documents_titu_compara = mongo.db.asignaturas.distinct("titulo", {"universidad": data_selected["universidadCompara"], "area": data_selected["areaCompara"]}) 
    # copiado 
        lista_asignaturas = []

        asignaturas = asignaturas_universidad(data_selected["universidad"],data_selected["area"],data_selected["titulo"])        
        for asignatura in asignaturas:
            lista_asignaturas.append(asignatura.get('_id', ''))
        query_competencias = { '$and': [
            {"course_id": { "$in": lista_asignaturas}}, 
            {'correccion':{'$exists': True}}, 
            {'correccion': {'$ne': '-1'}}
            ] }
        
        
        lista_asignaturas_compara = []
        query_competencias_compara = { '$and': [
            {"course_id": { "$in": lista_asignaturas}}, 
            {'correccion':{'$exists': True}}, 
            {'correccion': {'$ne': '-1'}}
            ] }

        asignaturas_compara = asignaturas_universidad(data_selected["universidadCompara"],data_selected["areaCompara"],data_selected["tituloCompara"])        
        for asignatura in asignaturas_compara:
            lista_asignaturas_compara.append(asignatura.get('_id', ''))
        query_competencias_compara = { '$and': [
            {"course_id": { "$in": lista_asignaturas_compara}}, 
            {'correccion':{'$exists': True}}, 
            {'correccion': {'$ne': '-1'}}
            ] }
        
        data = {
            'competencias': {
                'registradas': mongo.db.competencias.count_documents(query_competencias),
                'correccion': report_correccion(lista_asignaturas, "competencias"),
                'cognitivo': report_cognitivo(lista_asignaturas, "competencias"),
                'estructura': report_estructura(lista_asignaturas, "competencias"),
                'afectivo': report_afectivo(lista_asignaturas, "competencias"),
                'tecnologico': report_tecnologico(lista_asignaturas, "competencias"),
                'colaborativo': report_colaborativo(lista_asignaturas, "competencias")
            },
            'competencias_compara': {
                'registradas': mongo.db.competencias.count_documents(query_competencias_compara),
                'correccion': report_correccion(lista_asignaturas_compara, "competencias"),
                'cognitivo': report_cognitivo(lista_asignaturas_compara, "competencias"),
                'estructura': report_estructura(lista_asignaturas_compara, "competencias"),
                'afectivo': report_afectivo(lista_asignaturas_compara, "competencias"),
                'tecnologico': report_tecnologico(lista_asignaturas_compara, "competencias"),
                'colaborativo': report_colaborativo(lista_asignaturas_compara, "competencias")
            }
        }

        #data['competencias']['pendientes'] = int(data['competencias']['total']) - int(data['competencias']['registradas'])
        #data['universidad'] = universidad 
    # fin copiado
    
    
    
    
    else:
        data_selected = {}
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        documents_area = {}
        documents_titu = {}
        documents_area_compara = {}
        documents_titu_compara = {}
        data = {}

    return render_template('report_combinacion.html', universidades = documents_unis, areas = documents_area, 
    titulos = documents_titu, areasCompara = documents_area_compara, titulosCompara = documents_titu_compara,  selected = data_selected, 
    data = data)

@app.route('/informes_competencias')
@app.route('/informes_competencias', methods=['POST'])
def informes_competencias():
    if 'username' not in session:
        return login(0)
    
    # Consultas comprobacion datos insertados
    # correccion -1 son aquellos entes cuya correccion no se ha definido entre los valores esperados
    # por tanto, se consideran no valoradas aunque existan otros campos
    query_competencias = { '$and': [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}] }
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
    

    data = {
        'competencias': {
            'registradas': mongo.db.competencias.count_documents(query_competencias),
            'total': mongo.db.competencias.count_documents(query),
            'correccion': report_correccion(lista_asignaturas, "competencias"),
            'cognitivo': report_cognitivo(lista_asignaturas, "competencias"),
            'estructura': report_estructura(lista_asignaturas, "competencias"),
            'afectivo': report_afectivo(lista_asignaturas, "competencias"),
            'tecnologico': report_tecnologico(lista_asignaturas, "competencias"),
            'colaborativo': report_colaborativo(lista_asignaturas, "competencias")
        }
    } 

    data['competencias']['pendientes'] = int(data['competencias']['total']) - int(data['competencias']['registradas'])
    data['universidad'] = universidad 
   
    return render_template('report_competencias.html', universidades = documents_unis, selected = {'universidad': universidad}, data = data)

@app.route('/informes_resultados')
@app.route('/informes_resultados', methods=['POST'])
def informes_resultados():
    if 'username' not in session:
        return login(0)

    # Consultas comprobacion datos insertados
    # correccion -1 son aquellos entes cuya correccion no se ha definido entre los valores esperados
    # por tanto, se consideran no valoradas aunque existan otros campos
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
        
        query_resultados['course_id'] = query['course_id']
    

    data = {
        'resultados': {
            'registrados': mongo.db.resultados.count_documents(query_resultados),
            'total': mongo.db.resultados.count_documents(query),
            'correccion': report_correccion(lista_asignaturas, "resultados"),
            'cognitivo': report_cognitivo(lista_asignaturas, "resultados"),
            'estructura': report_estructura(lista_asignaturas, "resultados"),
            'afectivo': report_afectivo(lista_asignaturas, "resultados"),
            'tecnologico': report_tecnologico(lista_asignaturas, "resultados"),
            'colaborativo': report_colaborativo(lista_asignaturas, "resultados")
        }
    } 

    data['resultados']['pendientes'] = int(data['resultados']['total']) - int(data['resultados']['registrados'])
    data['universidad'] = universidad 
   
    return render_template('report_resultados.html', universidades = documents_unis, selected = {'universidad': universidad}, data = data)


@app.route('/informes_medios')
@app.route('/informes_medios', methods=['POST'])
def informes_medios():
    if 'username' not in session:
        return login(0)

    # Consultas comprobacion datos insertados
    # correccion -1 son aquellos entes cuya correccion no se ha definido entre los valores esperados
    # por tanto, se consideran no valoradas aunque existan otros campos
    query_medios = { '$and': [{'correccion':{'$exists': True}}, {'correccion': {'$ne': '-1'}}] }
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
        
        query_medios['course_id'] = query['course_id']
    

    data = {
        'medios': {
            'registrados': mongo.db.instrumentos.count_documents(query_medios),
            'total': mongo.db.instrumentos.count_documents(query),
            'correccion': report_correccion(lista_asignaturas, "medios")
        }
    } 

    data['medios']['pendientes'] = int(data['medios']['total']) - int(data['medios']['registrados'])
    data['universidad'] = universidad 
   
    return render_template('report_medios.html', universidades = documents_unis, selected = {'universidad': universidad}, data = data)



def report_afectivo(lista_asignaturas, element):    
    if(len(lista_asignaturas)==0):
        pipeline = [
                {
                    "$match":
                    {
                        "afectivo": { "$exists":"true"}
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$afectivo",
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
    else:
        pipeline = [
                {
                    "$match":
                    {
                        "$and":
                        [
                            {"course_id":
                            {
                                "$in": lista_asignaturas
                            }},
                            {"afectivo": { "$exists":"true"}}
                        ]
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$afectivo",
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

    if element == "resultados":
        data = mongo.db.resultados.aggregate(pipeline)
    else: # competencias
        data = mongo.db.competencias.aggregate(pipeline)

    lista_afectivo = {0:0, 1:0}
    for tipo in data:
            lista_afectivo[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_afectivo

def report_tecnologico(lista_asignaturas, element):    
    if(len(lista_asignaturas)==0):
        pipeline = [
                {
                    "$match":
                    {
                        "tecnologico": { "$exists":"true"}
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$tecnologico",
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
    else:
        pipeline = [
                {
                    "$match":
                    {
                        "$and":
                        [
                            {"course_id":
                            {
                                "$in": lista_asignaturas
                            }},
                            {"tecnologico": { "$exists":"true"}}
                        ]
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$tecnologico",
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

    if element == "resultados":
        data = mongo.db.resultados.aggregate(pipeline)
    else: # competencias
        data = mongo.db.competencias.aggregate(pipeline)

    lista_tecnologico = {0:0, 1:0}
    for tipo in data:
            lista_tecnologico[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_tecnologico

def report_colaborativo(lista_asignaturas, element):    
    if(len(lista_asignaturas)==0):
        pipeline = [
                {
                    "$match":
                    {
                        "colaborativo": { "$exists":"true"}
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$colaborativo",
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
    else:
        pipeline = [
                {
                    "$match":
                    {
                        "$and":
                        [
                            {"course_id":
                            {
                                "$in": lista_asignaturas
                            }},
                            {"colaborativo": { "$exists":"true"}}
                        ]
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$colaborativo",
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

    if element == "resultados":
        data = mongo.db.resultados.aggregate(pipeline)
    else: # competencias
        data = mongo.db.competencias.aggregate(pipeline)

    lista_colaborativo = {0:0, 1:0}
    for tipo in data:
            lista_colaborativo[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_colaborativo

def report_cognitivo(lista_asignaturas, element):
    if(len(lista_asignaturas)==0):
        pipeline = [
                {
                    "$match":
                    {
                        "cognitivo": { "$exists":"true"}
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$cognitivo",
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
    else:
        pipeline = [
                {
                    "$match":
                    {
                        "$and":
                        [
                            {"course_id":
                            {
                                "$in": lista_asignaturas
                            }},
                            {"cognitivo": { "$exists":"true"}}
                        ]
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$cognitivo",
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

    if element == "resultados":
        data = mongo.db.resultados.aggregate(pipeline)
    else: # competencias
        data = mongo.db.competencias.aggregate(pipeline)

    lista_cognitivo = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    for tipo in data:
            lista_cognitivo[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_cognitivo

def report_correccion(lista_asignaturas,element):
    if(len(lista_asignaturas)==0):
        pipeline = [
                {
                    "$match":
                    {
                        "correccion": { "$exists":"true"}
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$correccion",
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
    else:
        pipeline = [
                {
                    "$match":
                    {
                        "$and":
                        [
                            {"course_id":
                            {
                                "$in": lista_asignaturas
                            }},
                            {"correccion": { "$exists":"true"}}
                        ]
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$correccion",
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

    if element == "resultados":
        data = mongo.db.resultados.aggregate(pipeline)
    elif element == "medios":
        data = mongo.db.instrumentos.aggregate(pipeline)
    else: # competencias
        data = mongo.db.competencias.aggregate(pipeline)

    # Tipos de corrección
    lista_correccion = {
        -1: 0,
        0: 0,
        1: 0,
        2: 0
    }

    # el tipo -1 está fastidiando. INVESTIGAR. EN OVIEDO SOLO SALEN DOS TIPOS!
    for tipo in data:
            lista_correccion[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_correccion

def report_estructura(lista_asignaturas, element):
    if(len(lista_asignaturas)==0):
        pipeline = [
                {
                    "$match":
                    {
                        "estructura": { "$exists":"true"}
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$estructura",
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
    else:
        pipeline = [
                {
                    "$match":
                    {
                        "$and":
                        [
                            {"course_id":
                            {
                                "$in": lista_asignaturas
                            }},
                            {"estructura": { "$exists":"true"}}
                        ]
                    }
                },
                {
                    "$group": 
                    {
                        "_id": "$estructura",
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



    if element == "resultados":
        data = mongo.db.resultados.aggregate(pipeline)
    else: # competencias
        data = mongo.db.competencias.aggregate(pipeline)

    lista_estructura = {1:0, 2:0, 3:0, 4:0, 5:0}
    for tipo in data:
            lista_estructura[int(tipo.get('_id', ''))] = tipo.get('count', '')
    
    return lista_estructura

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

import os
	
if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug = True)
    #app.run(port = 3000, debug = True)
