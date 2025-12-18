import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
import logging
from flask import Flask, send_from_directory, request

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
app.logger.setLevel(logging.INFO)


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/index2")
def home_index2():
    return send_from_directory(FRONTEND_DIR, "index2.html")

@app.route("/espaces")
def espaces():
    return send_from_directory(FRONTEND_DIR, "espaces.html")


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(FRONTEND_DIR / "assets", filename)

def _smtp_settings():
    return {
        "host": os.environ.get("SMTP_HOST"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER"),
        "password": os.environ.get("SMTP_PASSWORD"),
        "sender": os.environ.get("SMTP_FROM") or os.environ.get("SMTP_USER"),
        "recipient": os.environ.get("SMTP_TO"),
        "starttls": os.environ.get("SMTP_STARTTLS", "true").lower() != "false",
    }


def send_form_email(form_name: str, payload: dict) -> tuple[bool, str | None]:
    settings = _smtp_settings()
    missing = [key for key in ("host", "sender", "recipient") if not settings.get(key)]
    if missing:
        msg = f"SMTP non configuré, champs manquants: {', '.join(missing)}"
        app.logger.warning(msg)
        return False, msg

    email = EmailMessage()
    email["Subject"] = f"[Plaisir partagé] Nouvelle demande ({form_name})"
    email["From"] = settings["sender"]
    email["To"] = settings["recipient"]
    email.set_content(
        "Nouveau formulaire reçu.\n\n"
        f"Type: {form_name}\n\n"
        f"Payload JSON:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
    )

    try:
        with smtplib.SMTP(settings["host"], settings["port"]) as server:
            if settings["starttls"]:
                server.starttls(context=ssl.create_default_context())
            if settings["user"] and settings["password"]:
                server.login(settings["user"], settings["password"])
            server.send_message(email)
        return True, None
    except Exception as exc:
        app.logger.exception("Impossible d'envoyer l'email %s", form_name)
        return False, str(exc)


def handle_form_submission(form_name: str):
    payload = request.get_json(silent=True) or {}
    app.logger.info("%s payload: %s", form_name, payload)

    sent, error = send_form_email(form_name, payload)
    status = 200 if sent else 500
    response = {"success": sent}
    if not sent and error:
        response["error"] = error
    return response, status


@app.route("/api/contact", methods=["POST"])
def contact():
    return handle_form_submission("Contact")


@app.route("/api/espaces", methods=["POST"])
def espaces_form():
    return handle_form_submission("Espaces")


@app.route("/api/artistes", methods=["POST"])
def artistes_form():
    return handle_form_submission("Artistes")


@app.route("/api/projets", methods=["POST"])
def projets_form():
    return handle_form_submission("Projets")
