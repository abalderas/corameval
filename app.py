from flask import Flask, render_template, url_for, request, jsonify, json, session
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from flask_bcrypt import bcrypt

app = Flask(__name__)

# MongoDB local connection
#app.config['MONGO_URI'] = 'mongodb://skillsapp:UCa2019psi@localhost:27017/skillsdb'
#mongo = PyMongo(app)


# MondoDB Atlas Remote Connection
mongo = pymongo.MongoClient("mongodb+srv://CORAMevalDBUser:donx7Xb6uGFKMbUL@cluster0-cz4qg.mongodb.net/test?retryWrites=true&w=majority")
mongo.db = mongo.skillsdb

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
    session.pop('username')

    return login(0)

@app.route('/access', methods=['POST'])
def access():   
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})    

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return Index()
        return login(1)
    return login(2)


@app.route('/')
def Index():
    if 'username' not in session:
        return login(0)

    documents_unis = mongo.db.asignaturas.distinct("universidad")
    selected_uni = documents_unis[0]
    documents_area = mongo.db.asignaturas.distinct("area", {"universidad": selected_uni})
    selected_area = documents_area[0]
    documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": selected_uni, "area": selected_area}) 
    selected_titu = documents_titu[0]
    documents_nivel1 = mongo.db.asignaturas.distinct("nivel1", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu})
    selected_nivel1 = documents_nivel1[0]
    documents_nivel2 = mongo.db.asignaturas.distinct("nivel2", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1})
    selected_nivel2 = documents_nivel2[0]
    documents_cour = mongo.db.asignaturas.distinct("asignatura", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1, "nivel2": selected_nivel2})
    selected_cour = documents_cour[0]
    document_detl = mongo.db.asignaturas.find_one({"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1, "nivel2": selected_nivel2, "asignatura": selected_cour}, {"creditos":1, "tipo":1}) 
    data_selected = {
        'universidad': selected_uni,
        'area': selected_area,
        'titulo': selected_titu,
        'nivel1': selected_nivel1,
        'nivel2': selected_nivel2,
        'asignatura': selected_cour,
        'tipo': document_detl['tipo'],
        'creditos': document_detl['creditos']
        }
    return render_template('index.html', universidades = documents_unis, areas = documents_area, titulos = documents_titu, niveles1 = documents_nivel1, niveles2 = documents_nivel2, asignaturas = documents_cour, selected = data_selected)

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
    nivel1 = request.form['nivel1']

    documents_cour = mongo.db.asignaturas.distinct("nivel2", {"universidad": universidad, "area": area, "titulo": degree, "nivel1": nivel1}) 

    return jsonify(documents_cour)


@app.route('/listing_courses', methods=['POST'])
def listing_courses():
    universidad = request.form['universidad']
    area = request.form['area']
    degree = request.form['degree']
    nivel1 = request.form['nivel1']
    nivel2 = request.form['nivel2']

    documents_cour = mongo.db.asignaturas.distinct("asignatura", {"universidad": universidad, "area": area, "titulo": degree, "nivel1": nivel1, "nivel2": nivel2}) 

    return jsonify(documents_cour)

    
@app.route('/listing_details', methods=['POST'])
def listing_details():
    universidad = request.form['universidad']
    area = request.form['area']
    degree = request.form['degree']
    nivel1 = request.form['nivel1']
    nivel2 = request.form['nivel2']
    course = request.form['course']

    document_detl = mongo.db.asignaturas.find_one({"universidad": universidad, "area": area, "titulo": degree, "nivel1": nivel1, "nivel2": nivel2, "asignatura": course}, {"creditos":1, "tipo":1}) 

    data = {'tipo': document_detl['tipo'], 'creditos': document_detl['creditos']}

    return jsonify(data)

    # -------------------------------------------------------------------------
    # Final del bloque de AJAX
    # -------------------------------------------------------------------------

@app.route('/buscar', defaults={'id': 0}, methods=['POST'])
@app.route('/buscar/<id>')
def buscar(id):

    if id != 0:
        document_detl = mongo.db.asignaturas.find_one({"_id": ObjectId(id)}, {"universidad": 1, "area": 1, "titulo": 1,
         "nivel1":1, "nivel2": 1, "asignatura": 1, "_id": 1, "creditos":1, "tipo":1})
        print(id)
        data_selected = {
            'universidad': document_detl['universidad'],
            'area': document_detl['area'],
            'titulo': document_detl['titulo'],
            'nivel1': document_detl['nivel1'],
            'nivel2': document_detl['nivel2'],
            'asignatura': document_detl['asignatura'],
            'tipo': document_detl['tipo'],
            'creditos': document_detl['creditos']
            }
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": document_detl['universidad'], "area": document_detl['area']})
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        #documents_area = mongo.db.asignaturas.distinct("area")
        # documents_unis = mongo.db.asignaturas.distinct("universidad")
        # selected_uni = request.form['university']
        documents_area = mongo.db.asignaturas.distinct("area", {"universidad": document_detl['universidad']})
        # selected_area = request.form['area']
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": document_detl['universidad'], "area": document_detl['area']}) 
        #selected_titu = request.form['titulo']
        documents_nivel1 = mongo.db.asignaturas.distinct("nivel1", {"universidad": document_detl['universidad'], "area": document_detl['area'], "titulo": document_detl['titulo']})
        documents_nivel2 = mongo.db.asignaturas.distinct("nivel2", {"universidad": document_detl['universidad'], "area": document_detl['area'], "titulo": document_detl['titulo'], "nivel1": document_detl['nivel1']})
        documents_cour = mongo.db.asignaturas.distinct("asignatura", {"universidad": document_detl['universidad'], "area": document_detl['area'], "titulo": document_detl['titulo'], "nivel1": document_detl['nivel1'], "nivel2": document_detl['nivel2']}) 
        # selected_cour = request.form['asignatura']
        
    else:
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": request.form['university'], "area": request.form['area']})
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        documents_area = mongo.db.asignaturas.distinct("area")
        documents_unis = mongo.db.asignaturas.distinct("universidad")
        selected_uni = request.form['university']
        documents_area = mongo.db.asignaturas.distinct("area", {"universidad": selected_uni})
        selected_area = request.form['area']
        documents_titu = mongo.db.asignaturas.distinct("titulo", {"universidad": selected_uni, "area": selected_area}) 
        selected_titu = request.form['titulo']
        documents_nivel1 = mongo.db.asignaturas.distinct("nivel1", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu})
        selected_nivel1 = request.form['nivel1']
        documents_nivel2 = mongo.db.asignaturas.distinct("nivel2", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1})
        selected_nivel2 = request.form['nivel2']
        documents_cour = mongo.db.asignaturas.distinct("asignatura", {"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1, "nivel2": selected_nivel2})
        selected_cour = request.form['asignatura']
        document_detl = mongo.db.asignaturas.find_one({"universidad": selected_uni, "area": selected_area, "titulo": selected_titu, "nivel1": selected_nivel1, "nivel2": selected_nivel2, "asignatura": selected_cour}, {"creditos":1, "tipo":1}) 
        data_selected = {
            'universidad': selected_uni,
            'area': selected_area,
            'titulo': selected_titu,
            'nivel1': selected_nivel1,
            'nivel2': selected_nivel2,
            'asignatura': selected_cour,
            'tipo': document_detl['tipo'],
            'creditos': document_detl['creditos']
            }
        

    # skills
    course_id = document_detl['_id']
    documents_skills = mongo.db.competencias.find({"course_id": course_id}).sort("name",1)
    documents_results = mongo.db.resultados.find({"course_id": course_id}).sort("name",1)
    documents_instruments = mongo.db.instrumentos.find({"course_id": course_id}).sort("name",1)

    return render_template('index.html', universidades = documents_unis, areas = documents_area, titulos = documents_titu, 
        niveles1 = documents_nivel1, niveles2 = documents_nivel2, asignaturas = documents_cour, selected = data_selected, 
        skills = documents_skills, results = documents_results, instruments = documents_instruments)


@app.route('/skill/<id>', defaults={'save':0})
@app.route('/skill/<id>/<save>')
def skill(id, save):
    # obtenemos id del curso
    document_skill = mongo.db.competencias.find_one({"_id": ObjectId(id)}, {"course_id":1, "name":1, "tipo": 1, 
        "correccion":1, "cognitivo":1, "factual": 1, "conceptual":1, "procedimental": 1, "metacognitivo":1,
        "estructura":1, "afectivo":1, "tecnologico":1, "colaborativo":1}) 
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
        "tecnologico":1, "colaborativo":1}) 
    data_course = institution(document_result['course_id'])

    documents_all_results = mongo.db.resultados.find({"course_id": document_result['course_id']}).sort("name",1)

    return render_template('results.html', course = data_course, results = documents_all_results, document = document_result, save = save)

@app.route('/instrument/<id>', defaults={'save':0})
@app.route('/instrument/<id>/<save>')
def instrument(id, save):
    # obtenemos id del curso
    documents_instrument = mongo.db.instrumentos.find_one({"_id": ObjectId(id)}, {"course_id":1, "name":1, "correccion": 1, "autenticidad": 1}) 
    data_course = institution(documents_instrument['course_id'])

    documents_all_instruments = mongo.db.instrumentos.find({"course_id": documents_instrument['course_id']}).sort("name",1)

    return render_template('instruments.html', course = data_course, instruments = documents_all_instruments, document = documents_instrument, save = save)

@app.route('/instrument/save/', defaults={'id': 0}, methods=['POST'])
@app.route('/instrument/save/<id>')
def instrument_save(id):
    myquery = { "_id": ObjectId(request.form['id']) }
    newvalues = { "$set": { "correccion": request.form['correccion'], "autenticidad": request.form['autenticidad'] } }

    mongo.db.instrumentos.update_one(myquery, newvalues)
    save = 1
    return instrument(request.form['id'], save)

@app.route('/skill/save/', defaults={'id': 0}, methods=['POST'])
@app.route('/skill/save/<id>')
def skill_save(id):
    myquery = { "_id": ObjectId(request.form['id']) }
    newvalues = { "$set": {     "tipo": request.form['tipo'],
                                "correccion": request.form['correccion'], 
                                "cognitivo": request.form['cognitivo'],
                                "factual": request.form['factual'],
                                "conceptual": request.form['conceptual'],
                                "procedimental": request.form['procedimental'],
                                "metacognitivo": request.form['metacognitivo'],
                                "estructura": request.form['estructura'],
                                "afectivo": request.form['afectivo'],
                                "tecnologico": request.form['tecnologico'],
                                "colaborativo": request.form['colaborativo'] } }

    mongo.db.competencias.update_one(myquery, newvalues)
    save = 1
    return skill(request.form['id'], save)

@app.route('/result/save/', defaults={'id': 0}, methods=['POST'])
@app.route('/result/save/<id>')
def result_save(id):
    myquery = { "_id": ObjectId(request.form['id']) }
    newvalues = { "$set": {     "correccion": request.form['correccion'], 
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
                                "colaborativo": request.form['colaborativo'] } }

    mongo.db.resultados.update_one(myquery, newvalues)
    save = 1
    return result(request.form['id'], save)

def institution(id):
    document_institution = mongo.db.asignaturas.find_one({"_id": id})
    
    data_course = {
        'universidad': document_institution['universidad'],
        'area': document_institution['area'],
        'titulo': document_institution['titulo'],
        'nivel1': document_institution['nivel1'],
        'nivel2': document_institution['nivel2'],
        'asignatura': document_institution['asignatura'],
        'tipo': document_institution['tipo'],
        'creditos': document_institution['creditos'],
        "_id": document_institution['_id']
        }
    print()
    return data_course

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
    with open('data/upv_competencias.csv', newline='') as File:
        reader = csv.reader(File, delimiter=':')
        
        for row in reader:
            counter = counter + 1
            data_course = {
                'universidad': row[0],
                'area': row[1],
                'titulo': row[2],
                'nivel1': row[3],
                'nivel2': row[4],
                'asignatura': row[5],
                'tipo': row[7],
                'creditos': row[6]
                }
            existe_institucion = mongo.db.asignaturas.find_one(data_course)
            if (not(existe_institucion)):
                nuevo = mongo.db.asignaturas.insert_one(data_course)
                id_institucion = nuevo.inserted_id
            else:
                id_institucion = existe_institucion['_id']
            
            data_competencia = {
                'course_id': id_institucion,
                'name': row[8],
                'tipo': tipo_competencia(row[9]),
                'observaciones': row[10]
            }
            print(str(counter))
            existe_competencia = mongo.db.competencias.find_one(data_competencia)
            if(not(existe_competencia)):
                mongo.db.competencias.insert_one(data_competencia)

    return 'COMPETENCIAS CARGADAS!'

@app.route('/cargar_resultados')
def cargar_resultados():
    import csv
    counter = 1
    with open('data/upv_resultados.csv', newline='') as File:
        reader = csv.reader(File, delimiter=':')
        
        for row in reader:
            counter = counter + 1
            
            data_course = {
                'universidad': row[0],
                'area': row[1],
                'titulo': row[2],
                'nivel1': row[3],
                'nivel2': row[4],
                'asignatura': row[5],
                'creditos': row[6],
                'tipo': row[7]                
                }
            existe_asignatura = mongo.db.asignaturas.find_one(data_course)
            if (not(existe_asignatura)):
                #nuevo = mongo.db.asignaturas.insert_one(data_course)
                #id_asignatura = nuevo.inserted_id
                print(str(counter) + " no existe asignatura")
                print(data_course)
            else:
                id_asignatura = existe_asignatura['_id']
            
            data_resultado = {
                'course_id': id_asignatura,
                'name': row[8],
                'observaciones': row[9]
            }
            
            # REVISAR UPV RESULTADOS ...
            print(counter)
            if (data_resultado['name'] != "NO APARECE" and data_resultado['name'] != ""):
                #print(str(counter) + " no existe resultado")
                existe_resultado = mongo.db.resultados.find_one(data_resultado)
                if(not(existe_resultado)):
                    mongo.db.resultados.insert_one(data_resultado)

    return 'RESULTADOS CARGADOS!'

@app.route('/cargar_instrumentos')
def cargar_instrumentos():
    import csv
    counter = 1
    with open('data/upv_instrumentos.csv', newline='') as File:
        reader = csv.reader(File, delimiter=':')
        
        for row in reader:
            counter = counter + 1
            
            data_course = {
                'universidad': row[0],
                'area': row[1],
                'titulo': row[2],
                'nivel1': row[3],
                'nivel2': row[4],
                'asignatura': row[5],
                'creditos': row[6],
                'tipo': row[7]                
                }
            existe_asignatura = mongo.db.asignaturas.find_one(data_course)
            
            if (not(existe_asignatura)):
                nuevo = mongo.db.asignaturas.insert_one(data_course)
                id_asignatura = nuevo.inserted_id
                print(str(counter) + " asignatura nueva")
            else:
                id_asignatura = existe_asignatura['_id']
            
            data_instrumento = {
                'course_id': id_asignatura,
                'name': row[8],
                'observaciones': row[11]
            }
            
            #print(counter)
            if (data_instrumento['name'] != "NO APARECE" and data_instrumento['name'] != ""):
                #print(str(counter) + " no existe resultado")
                existe_instrumento = mongo.db.instrumentos.find_one(data_instrumento)
                if(not(existe_instrumento)):
                    mongo.db.instrumentos.insert_one(data_instrumento)

    return 'INSTRUMENTOS CARGADOS!'

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

if __name__ == '__main__':
    app.run(port = 3000, debug = True)