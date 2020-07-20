# Proyecto para el control de consumo de vasos

# Librerías
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime, timedelta

# Conexión a MONGODB + Base de datos + Colección
MONGO_URL_ATLAS = 'mongodb+srv://rafel:Root12345@cluster0-l376h.mongodb.net/test?retryWrites=true&w=majority'
cliente = MongoClient(MONGO_URL_ATLAS, ssl_cert_reqs=False)
db = cliente['db_consumo_H2O_dia']
coleccion = db['c_consumoH2O_dia']

app = Flask(__name__)

# Creación de rutas

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('index.html')

@app.route("/ruta_entrar-nuevo-registro-dia")
def entrarNuevoRegistroDia():
    return render_template('entrar_nuevo_registro_dia.html', fecha_actual=datetime.utcnow())

@app.route("/ruta_crear-nuevo-registro-dia", methods=['GET', 'POST'])
def crearNuevoRegistroDia():
    if request.method == 'POST':
        try:
            fecha_consumo = request.form['fecha_consumo']
            # Hacemos la conversión de texto a coma flotante (será el valor 0 en caso de imposibilidad)
            vasos_manana = convert_to_float(request.form['vasos_manana'], 0.0)
            vasos_mediodia = convert_to_float(request.form['vasos_mediodia'], 0.0)
            vasos_tarde = convert_to_float(request.form['vasos_tarde'], 0.0)
            vasos_noche = convert_to_float(request.form['vasos_noche'], 0.0)
            # Calculamos la suma total de vasos consumidos
            vasos_total_dia = vasos_manana +  vasos_mediodia +  vasos_tarde +  vasos_noche
            volumen_total_dia = vasos_total_dia * 0.2
            nuevo_registro_dia = {"fecha_consumo": fecha_consumo, "vasos_manana": vasos_manana,
                            "vasos_mediodia": vasos_mediodia, "vasos_tarde": vasos_tarde, "vasos_noche": vasos_noche, "vasos_total_dia": vasos_total_dia, "volumen_total_dia":volumen_total_dia}
            coleccion.insert_one(nuevo_registro_dia)
            return redirect(url_for('entrarNuevoRegistroDia'))
        except ValueError:
            raise Exception("Valor no posible conversion")
    return redirect(url_for('entrarNuevoRegistroDia'))

@app.route("/ruta_listar-registros")
def listarRegistros():
    datos_para_listar = coleccion.find()
    titulo_listado = "Recopilación de consumos"
    return render_template('listado_registros.html', datos_para_listar=datos_para_listar, titulo_listado=titulo_listado)


@app.route("/ruta_editar/<id>")
def editarConsumo(id):
    buscarPorId = {"_id": ObjectId(id)}
    datos_para_editar = coleccion.find_one(buscarPorId)
    return render_template('/editar.html', datos_para_editar=datos_para_editar)


@app.route("/ruta_editar_confirmado", methods=['GET', 'POST'])
def actualizarConsumo():
    if request.method == 'POST':
        try:
            fecha_consumo = request.form['fecha_consumo']
            vasos_manana = convert_to_float(request.form['vasos_manana'], 0.0)
            vasos_mediodia = convert_to_float(request.form['vasos_mediodia'], 0.0)
            vasos_tarde = convert_to_float(request.form['vasos_tarde'], 0.0)
            vasos_noche = convert_to_float(request.form['vasos_noche'], 0.0)
            vasos_total_dia = vasos_manana + vasos_mediodia + vasos_tarde + vasos_noche
            volumen_total_dia = vasos_total_dia * 0.2
            registroEditado = {"fecha_consumo": fecha_consumo, "vasos_manana": vasos_manana,
                                "vasos_mediodia": vasos_mediodia, "vasos_tarde": vasos_tarde, "vasos_noche": vasos_noche, "vasos_total_dia": vasos_total_dia, "volumen_total_dia": volumen_total_dia}
            buscarPorId = {"_id": ObjectId(request.form["id"])}
            coleccion.update_one(buscarPorId, {"$set": registroEditado})
            return redirect(url_for('listarRegistros'))
        except ValueError:
            raise Exception("Error: Por algún motivo no se puede realizar la conversión del valor a coma flotante.")
    return redirect(url_for('listarRegistros'))

@app.route("/ruta_borrar/<id>")
def borrarConsumo(id):
    buscarPorId = {"_id": ObjectId(id)}
    datos_para_borrar = coleccion.find_one(buscarPorId)
    return render_template('/borrar.html', datos_para_borrar=datos_para_borrar)


@app.route("/ruta_borrar_confirmado", methods=["POST"])
def confirmadoBorrado():
    buscarPorId = {"_id": ObjectId(request.form["id"]) }
    coleccion.delete_one(buscarPorId)
    return redirect(url_for('listarRegistros'))

def convert_to_float(valor, valor_por_defecto):
    try:
        return float(valor)
    except:
        return valor_por_defecto

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(host='0.0.0.0', port=port, debug=True)
