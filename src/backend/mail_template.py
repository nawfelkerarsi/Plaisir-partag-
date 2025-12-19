import html
import json
from datetime import datetime


def _format_name(payload: dict) -> str:
    first = payload.get("firstName") or payload.get("firstname") or ""
    last = payload.get("lastName") or payload.get("lastname") or ""
    full = f"{first} {last}".strip()
    return full or "Client"


def render_admin_email(form_name: str, payload: dict) -> tuple[str, str, str]:
    subject = f"[Plaisir partagé] Nouvelle demande ({form_name})"
    plain_body = (
        "Nouveau formulaire reçu.\n\n"
        f"Type: {form_name}\n\n"
        f"Payload JSON:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
    )

    rows = "".join(
        f"<tr><th align='left'>{html.escape(str(key))}</th>"
        f"<td>{html.escape(str(value))}</td></tr>"
        for key, value in payload.items()
    )
    html_body = f"""
    <html lang="fr">
      <body style="font-family: 'Helvetica Neue', Arial, sans-serif; background:#f8fafc; padding:32px; margin:0;">
        <table role="presentation" style="max-width:640px; margin:auto; background:#ffffff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 14px 40px rgba(0,0,0,0.08); overflow:hidden; position:relative;">
          <tr>
            <td style="padding:0; position:relative;">
              <div style="position:absolute; inset:0; pointer-events:none; background:radial-gradient(circle at 15% 20%, rgba(255,191,150,0.35), transparent 45%), radial-gradient(circle at 85% 80%, rgba(125,211,252,0.35), transparent 45%);"></div>
              <div style="position:relative; padding:22px 26px 18px;">
                <div style="display:flex; align-items:center; gap:10px; color:#0f172a; font-size:18px; font-weight:700; letter-spacing:0.2px;">
                  <span style="display:inline-block; width:8px; height:8px; border-radius:999px; background:#111827;"></span>
                  Nouvelle demande – {html.escape(form_name)}
                </div>
                <p style="margin:10px 0 0; color:#4b5563; font-size:14px;">Un visiteur a rempli le formulaire sur Plaisir partagé.</p>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:0 24px 6px;">
              <table style="width:100%; border-collapse:collapse; font-size:14px; color:#111827; background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; overflow:hidden;">
                {rows or "<tr><td style='color:#9ca3af; padding:12px;'>Aucune donnée</td></tr>"}
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:14px 24px; background:#f3f4f6; color:#6b7280; font-size:12px;">
              Message automatique · {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    return subject, plain_body, html_body


def render_client_email(form_name: str, payload: dict) -> tuple[str, str, str]:
    name = _format_name(payload)
    subject = "Nous avons bien reçu votre demande – Plaisir partagé"

    plain_body = (
        f"Bonjour {name},\n\n"
        "Merci pour votre message, il a bien été transmis à l'équipe Plaisir Partagé.\n"
        "Nous revenons vers vous rapidement.\n\n"
        f"Résumé rapide : {json.dumps(payload, ensure_ascii=False)}\n\n"
        "— L'équipe Plaisir Partagé"
    )

    rows = "".join(
        f"<tr><th align='left'>{html.escape(str(key))}</th>"
        f"<td>{html.escape(str(value))}</td></tr>"
        for key, value in payload.items()
    )

    html_body = f"""
    <html lang="fr">
      <body style="font-family: 'Helvetica Neue', Arial, sans-serif; background:#f8fafc; padding:32px; margin:0;">
        <table role="presentation" style="max-width:640px; margin:auto; background:#ffffff; border:1px solid #e5e7eb; border-radius:14px; box-shadow:0 14px 40px rgba(0,0,0,0.08); overflow:hidden; position:relative;">
          <tr>
            <td style="padding:0; position:relative;">
              <div style="position:absolute; inset:0; pointer-events:none; background:radial-gradient(circle at 12% 18%, rgba(254,215,170,0.4), transparent 42%), radial-gradient(circle at 88% 78%, rgba(125,211,252,0.4), transparent 45%);"></div>
              <div style="position:relative; padding:22px 26px 18px;">
                <p style="margin:0; text-transform:uppercase; letter-spacing:0.18em; font-size:11px; color:#6b7280;">Plaisir partagé</p>
                <div style="margin-top:6px; color:#0f172a; font-size:20px; font-weight:700; letter-spacing:0.2px;">
                  Nous avons bien reçu votre demande
                </div>
                <p style="margin:10px 0 0; color:#4b5563; font-size:14px;">Bonjour {html.escape(name)}, merci pour votre message. Nous revenons vers vous au plus vite.</p>
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:14px 24px; background:#f3f4f6; color:#6b7280; font-size:12px;">
              Merci pour votre confiance. — L'équipe Plaisir partagé
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    return subject, plain_body, html_body
