from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "sistema": "FallGuard",
        "status": "online"
    })


@app.route("/api/falls", methods=["POST"])
def register_fall():
    data = request.get_json()

    print("Evento recebido:")
    print(data)

    return jsonify({
        "mensagem": "Queda registrada com sucesso",
        "dados": data
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)