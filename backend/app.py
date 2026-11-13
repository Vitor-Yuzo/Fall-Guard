from flask import Flask, jsonify, request
import mysql.connector
from config import DB_CONFIG
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "sistema": "FallGuard",
        "status": "online"
    })


@app.route("/api/falls", methods=["POST"])
def register_fall():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"erro": "JSON inválido ou ausente"}), 400

    evento = data.get("evento")
    classe = data.get("classe")
    confianca = data.get("confianca")
    timestamp_evento = data.get("timestamp")

    if not evento or not classe or not timestamp_evento:
        return jsonify({
            "erro": "Campos obrigatórios: evento, classe e timestamp"
        }), 400

    conexao = None
    cursor = None

    try:
        conexao = get_db_connection()
        cursor = conexao.cursor()

        sql = """
            INSERT INTO falls
            (evento, classe, confianca, timestamp_evento)
            VALUES (%s, %s, %s, %s)
        """

        valores = (evento, classe, confianca, timestamp_evento)
        cursor.execute(sql, valores)
        conexao.commit()

        fall_id = cursor.lastrowid

        return jsonify({
            "mensagem": "Queda registrada com sucesso",
            "id": fall_id
        }), 201

    except mysql.connector.Error:
        app.logger.exception("Erro ao salvar evento no MySQL")
        return jsonify({
            "erro": "Não foi possível salvar o evento no banco de dados"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()

@app.route("/api/falls", methods=["GET"])
def list_falls():
    conexao = None
    cursor = None

    try:
        conexao = get_db_connection()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, evento, classe, confianca, timestamp_evento
            FROM falls
            ORDER BY timestamp_evento DESC
        """)

        quedas = cursor.fetchall()

        for queda in quedas:
            if queda["timestamp_evento"] is not None:
                queda["timestamp_evento"] = queda[
                    "timestamp_evento"
                ].strftime("%Y-%m-%d %H:%M:%S")

            if queda["confianca"] is not None:
                queda["confianca"] = float(queda["confianca"])

        return jsonify(quedas), 200

    except mysql.connector.Error:
        app.logger.exception("Erro ao consultar quedas no MySQL")
        return jsonify({
            "erro": "Não foi possível consultar as quedas"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
