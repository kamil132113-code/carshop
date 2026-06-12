import psycopg2
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.json.ensure_ascii = False

DB = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "postgres",
    "user":     "postgres",
    "password": "kamil1321",
}


def get_db():
    return psycopg2.connect(**DB)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cars")
def cars():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.brand, c.model, c.year, c.price, c.status, p.url
        FROM cars c
        LEFT JOIN photos p ON p.car_id = c.id AND p.is_main = TRUE
        WHERE c.status = 'available'
        ORDER BY c.price
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([{
        "id":     r[0],
        "brand":  r[1],
        "model":  r[2],
        "year":   r[3],
        "price":  float(r[4]),
        "status": r[5],
        "photo":  r[6],
    } for r in rows])


@app.route("/leads", methods=["POST"])
def create_lead():
    data   = request.get_json()
    name   = data.get("name", "").strip()
    phone  = data.get("phone", "").strip()
    car_id = data.get("car_id")

    if not name or not phone:
        return jsonify({"error": "Имя и телефон обязательны"}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO leads (name, phone, car_id) VALUES (%s, %s, %s)",
        (name, phone, car_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)