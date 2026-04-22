from flask import Flask, render_template, request, jsonify
from berechnung import berechne_einfeldtraeger

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/berechne", methods=["POST"])
def berechne():
    try:
        data = request.get_json()

        L = float(data["L"])
        q = float(data.get("q", 0))
        EI = float(data.get("EI", 0)) or None
        lasten_raw = data.get("lasten", [])

        if L <= 0:
            return jsonify({"error": "Balkenlänge muss größer 0 sein"}), 400

        lasten = []
        for last in lasten_raw:
            F = float(last["F"])
            a = float(last["a"])
            if a < 0 or a > L:
                return jsonify({"error": f"Lastangriffspunkt a={a} m liegt außerhalb des Balkens (0 … {L} m)"}), 400
            lasten.append((F, a))

        if not lasten and q == 0:
            return jsonify({"error": "Mindestens eine Last erforderlich"}), 400

        result = berechne_einfeldtraeger(L, lasten, q, EI)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
