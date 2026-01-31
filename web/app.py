from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from config import ADMIN_PASSWORD

app = Flask(__name__)
app.secret_key = "super_secret_key"

DB_PATH = "database/store.db"


# ---------------------- دیتابیس ----------------------

def db():
    return sqlite3.connect(DB_PATH)


# ---------------------- ورود ----------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/panel")
        else:
            return render_template("login.html", title="ورود", error="رمز اشتباه است")

    return render_template("login.html", title="ورود")


# ---------------------- خروج ----------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------------- داشبورد ----------------------

@app.route("/panel")
def panel():
    if "admin" not in session:
        return redirect("/")
    return render_template("panel.html", title="داشبورد")


# ---------------------- مدیریت محصولات ----------------------

@app.route("/products")
def products():
    if "admin" not in session:
        return redirect("/")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT id, image_url, download_link FROM single_products")
    single = cur.fetchall()

    cur.execute("SELECT id, image_url, download_link FROM multi_products")
    multi = cur.fetchall()

    conn.close()

    return render_template("products.html", title="مدیریت محصولات", single=single, multi=multi)


@app.route("/add", methods=["POST"])
def add():
    if "admin" not in session:
        return redirect("/")

    category = request.form["category"]
    image = request.form["image"]
    link = request.form["link"]

    table = "single_products" if category == "single" else "multi_products"

    conn = db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {table} (image_url, download_link) VALUES (?, ?)", (image, link))
    conn.commit()
    conn.close()

    return redirect("/products")


@app.route("/delete/<category>/<int:pid>")
def delete(category, pid):
    if "admin" not in session:
        return redirect("/")

    table = "single_products" if category == "single" else "multi_products"

    conn = db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id=?", (pid,))
    conn.commit()
    conn.close()

    return redirect("/products")


# ---------------------- سفارش‌ها ----------------------

@app.route("/orders")
def orders():
    if "admin" not in session:
        return redirect("/")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT id, user_id, category, product_id, status FROM orders ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()

    return render_template("orders.html", title="سفارش‌ها", orders=data)


# ---------------------- گزارش فروش ----------------------

@app.route("/report")
def report():
    if "admin" not in session:
        return redirect("/")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM sales_report")
    total = cur.fetchone()[0]

    conn.close()

    return render_template("report.html", title="گزارش فروش", total=total)


# ---------------------- API: ثبت سفارش جدید از بات ----------------------

@app.route("/api/new_order", methods=["POST"])
def api_new_order():
    data = request.json

    user_id = data["user_id"]
    category = data["category"]
    product_id = data["product_id"]

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO orders (user_id, category, product_id, status) VALUES (?, ?, ?, ?)",
        (user_id, category, product_id, "waiting_admin")
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# ---------------------- API: آپدیت وضعیت سفارش ----------------------

@app.route("/api/update_order", methods=["POST"])
def api_update_order():
    data = request.json

    order_id = data["order_id"]
    new_status = data["status"]

    conn = db()
    cur = conn.cursor()

    cur.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "updated"})


# ---------------------- API: ارسال لینک دانلود به کاربر ----------------------
# (فعلاً بدون ارسال به بات، تا Railway کرش نکند)

@app.route("/api/send_download", methods=["POST"])
def api_send_download():
    data = request.json
    return jsonify({"status": "sent"})


# ---------------------- تأیید سفارش از پنل ----------------------

@app.route("/confirm/<int:order_id>", methods=["POST"])
def confirm(order_id):
    if "admin" not in session:
        return redirect("/")

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT user_id, category, product_id FROM orders WHERE id=?", (order_id,))
    order = cur.fetchone()

    if not order:
        conn.close()
        return redirect("/orders")

    user_id, category, product_id = order

    table = "single_products" if category == "single" else "multi_products"
    cur.execute(f"SELECT download_link FROM {table} WHERE id=?", (product_id,))
    product = cur.fetchone()

    if not product:
        conn.close()
        return redirect("/orders")

    download_link = product[0]

    cur.execute("UPDATE orders SET status='completed' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()

    return redirect("/orders")


# ---------------------- اجرا ----------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
