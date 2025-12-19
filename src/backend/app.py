import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
import logging
from flask import Flask, send_from_directory, request
from mail_template import render_admin_email, render_client_email

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
LOG_DIR = BACKEND_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
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
    sender = os.environ.get("SMTP_FROM") or os.environ.get("SMTP_USER")
    return {
        "host": os.environ.get("SMTP_HOST"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER"),
        "password": os.environ.get("SMTP_PASSWORD"),
        "sender": sender,
        "recipient": os.environ.get("SMTP_TO") or sender,
        "starttls": os.environ.get("SMTP_STARTTLS", "true").lower() != "false",
    }


def _send_email(
    settings: dict,
    to_addr: str,
    subject: str,
    plain_body: str,
    html_body: str,
    tag: str,
    bcc: list[str] | None = None,
):
    app.logger.info(
        "Envoi email %s -> %s (host=%s port=%s starttls=%s)",
        tag,
        to_addr,
        settings["host"],
        settings["port"],
        settings["starttls"],
    )

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = settings["sender"]
    email["To"] = to_addr
    if bcc:
        email["Bcc"] = ", ".join(bcc)
    email["Content-Language"] = "fr"
    email.set_content(plain_body)
    if html_body:
        email.add_alternative(html_body, subtype="html")

    try:
        if settings["starttls"]:
            server = smtplib.SMTP(settings["host"], settings["port"], timeout=15)
            server.starttls(context=ssl.create_default_context())
        else:
            server = smtplib.SMTP_SSL(settings["host"], settings["port"], timeout=15)

        with server:
            if settings["user"] and settings["password"]:
                server.login(settings["user"], settings["password"])
            server.send_message(email)
        app.logger.info("Email '%s' envoyé avec succès à %s", tag, to_addr)
        return True, None
    except Exception as exc:
        app.logger.exception("Impossible d'envoyer l'email %s", tag)
        return False, str(exc)


def _send_client_ack(settings: dict, form_name: str, payload: dict):
    client_email = payload.get("email")
    if not client_email:
        app.logger.info("Pas d'email client fourni, accusé non envoyé.")
        return True, None
    subject, plain_body, html_body = render_client_email(form_name, payload)
    return _send_email(
        settings,
        client_email,
        subject,
        plain_body,
        html_body,
        tag="client",
        bcc=[settings["recipient"]] if settings.get("recipient") else None,
    )


def send_form_email(form_name: str, payload: dict) -> tuple[bool, str | None]:
    settings = _smtp_settings()
    missing = [key for key in ("host", "sender", "recipient") if not settings.get(key)]
    if missing:
        msg = f"SMTP non configuré, champs manquants: {', '.join(missing)}"
        app.logger.warning(msg)
        return False, msg

    subject, plain_body, html_body = render_admin_email(form_name, payload)
    sent_admin, error_admin = _send_email(
        settings,
        settings["recipient"],
        subject,
        plain_body,
        html_body,
        tag="admin",
    )
    if sent_admin:
        ack_ok, ack_error = _send_client_ack(settings, form_name, payload)
        if not ack_ok:
            app.logger.warning("Accusé client non envoyé: %s", ack_error)
    return sent_admin, error_admin


def handle_form_submission(form_name: str):
    payload = request.get_json(silent=True) or {}
    app.logger.info("%s payload: %s", form_name, payload)

    sent, error = send_form_email(form_name, payload)
    if sent:
        app.logger.info("%s: email envoyé", form_name)
    else:
        app.logger.error("%s: échec de l'envoi (%s)", form_name, error)
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
