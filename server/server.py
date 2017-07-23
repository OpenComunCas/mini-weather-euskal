from data import DaoMedidas
from flask import Flask,jsonify,request


app = Flask(__name__)
DAO = DaoMedidas()

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/insertar',methods=['POST'])
def insertar():
    datos = eval(request.data)["data"]
    DAO.insertar(datos)
    return "ok"

@app.route('/obtener')
def obtener():
    data = DAO.obtener_todos()
    return jsonify({"valores":data})

@app.route('/current')
def current():
    data = DAO.current()
    return jsonify(data)

app.run(host="0.0.0.0")
