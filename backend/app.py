import os
import sys
import socket
import subprocess
import threading
from flask import Flask, jsonify, request
import mysql.connector
from config import DB_CONFIG
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Gerenciamento do monitoramento
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONITOR_SCRIPT = os.path.join(
    PROJECT_DIR,
    "machine_learning",
    "monitoramento.py"
)

monitor_process = None
monitor_lock = threading.Lock()

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883


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

def verificar_mysql():
    conexao = get_db_connection()
    conexao.close()
    return True


def verificar_mqtt():
    with socket.create_connection(
        (MQTT_HOST, MQTT_PORT), timeout=2
    ):
        return True


@app.route("/api/system/start", methods=["POST"])
def start_system():
    global monitor_process

    with monitor_lock:
        try:
            verificar_mysql()
            verificar_mqtt()

            if monitor_process is not None and monitor_process.poll() is None:
                return jsonify({
                    "mensagem": "Monitoramento já está ativo"
                }), 200

            monitor_process = subprocess.Popen(
                [sys.executable, MONITOR_SCRIPT],
                cwd=PROJECT_DIR
            )

            return jsonify({
                "mensagem": "Monitoramento iniciado",
                "pid": monitor_process.pid
            }), 200

        except Exception as erro:
            app.logger.exception("Erro ao iniciar FallGuard")
            return jsonify({
                "erro": str(erro)
            }), 500


@app.route("/api/system/stop", methods=["POST"])
def stop_system():
    global monitor_process

    with monitor_lock:
        if monitor_process is None or monitor_process.poll() is not None:
            monitor_process = None
            return jsonify({
                "mensagem": "Monitoramento já está parado"
            }), 200

        monitor_process.terminate()

        try:
            monitor_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            monitor_process.kill()
            monitor_process.wait()

        monitor_process = None

        return jsonify({
            "mensagem": "Monitoramento encerrado"
        }), 200


@app.route("/api/system/status", methods=["GET"])
def system_status():
    global monitor_process

    mysql_status = False
    mqtt_status = False

    try:
        verificar_mysql()
        mysql_status = True
    except Exception:
        pass

    try:
        verificar_mqtt()
        mqtt_status = True
    except Exception:
        pass

    camera_status = (
        monitor_process is not None
        and monitor_process.poll() is None
    )

    return jsonify({
        "mysql": mysql_status,
        "mqtt": mqtt_status,
        "camera_yolo": camera_status,
        "sistema_ativo": camera_status
    }), 200

if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=5000,
    debug=True,
    use_reloader=False
)
