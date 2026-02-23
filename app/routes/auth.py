"""
Auth routes — /register, /login, /logout
"""
import functools
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, g,
)
from app.models.farmer import (
    create_farmer, get_farmer_by_username,
    get_farmer_by_id, verify_password,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Login required decorator ───────────────────────────────────────────────────

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.farmer is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


# ── Before request: load current farmer into g ─────────────────────────────────

@auth_bp.before_app_request
def load_logged_in_farmer():
    farmer_id = session.get("farmer_id")
    if farmer_id is None:
        g.farmer = None
    else:
        g.farmer = get_farmer_by_id(farmer_id)


# ── Register ───────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if g.farmer:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username  = request.form.get("username", "").strip()
        password  = request.form.get("password", "")
        confirm   = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()
        location  = request.form.get("location", "").strip()

        errors = []
        if not username:
            errors.append("Username is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if not full_name:
            errors.append("Full name is required.")
        if not location:
            errors.append("District/Location is required.")

        if not errors:
            farmer_id = create_farmer(username, password, full_name, location)
            if farmer_id == -1:
                flash("Username already taken. Please choose another.", "danger")
            else:
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("auth.login"))

        for err in errors:
            flash(err, "danger")

    return render_template("auth/register.html")


# ── Login ──────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.farmer:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        farmer = get_farmer_by_username(username)
        if farmer is None or not verify_password(farmer, password):
            flash("Invalid username or password.", "danger")
        else:
            session.clear()
            session["farmer_id"] = farmer["id"]
            flash(f"Welcome back, {farmer['full_name']}!", "success")
            return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


# ── Logout ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
