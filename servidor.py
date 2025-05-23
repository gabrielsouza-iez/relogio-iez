from flask import Flask, request, jsonify
from threading import Lock

app = Flask(__name__)

# Lista ordenada da direita para a esquerda
hosts = ["PC1", "PC2", "PC3", "PC4", "PC5"]
idx_atual = 0
lock = Lock()

@app.route("/quem_deve_exibir", methods=["GET"])
def quem_deve_exibir():
    host = request.args.get("host")
    with lock:
        dono = hosts[idx_atual]
        if host == dono:
            return jsonify({"exibir": True, "posicao_inicial": "direita"})
        else:
            return jsonify({"exibir": False})

@app.route("/janela_saiu", methods=["POST"])
def janela_saiu():
    global idx_atual
    data = request.json
    host = data.get("host")

    with lock:
        if hosts[idx_atual] != host:
            return jsonify({"status": "ignorado"})

        idx_atual = (idx_atual + 1) % len(hosts)
        proximo = hosts[idx_atual]
        print(f"Janela saiu de {host}, próxima parada: {proximo}")
        return jsonify({"status": "ok", "proximo": proximo})

@app.route("/estado", methods=["GET"])
def estado():
    with lock:
        return jsonify({
            "idx_atual": idx_atual,
            "atual": hosts[idx_atual],
            "ordem": hosts
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4044)
