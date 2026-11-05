import io
import csv
import os
import time

print("--- SLW BOOTH VIRTUAL CARD GENERATOR V2 STARTING ---", flush=True)

from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, StreamingResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
import qrcode

from app.card_store import card_store
from app.gemini_service import generate_persona_and_avatar

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(
    title="Google Cloud x Seoul - AI Virtual Business Card Generator",
    description="Interactive AI Virtual Business Card Generator powered by Google Cloud Gemini & Cloud Run",
    version="2.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


class CardGenerateRequest(BaseModel):
    name: str
    company: str
    role: str
    custom_role: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    lifestyle: List[str] = []
    theme: str = "gcloud"
    photo_base64: Optional[str] = None
    marketing_consent: bool = True

class PreviewRequest(BaseModel):
    photo_base64: str


from collections import defaultdict

DEMO_PASSCODE = os.environ.get("DEMO_PASSCODE", "")
ADMIN_PASSCODE = os.environ.get("ADMIN_PASSCODE", "SLW2026")
CARD_EXPIRATION_SECONDS = int(os.environ.get("CARD_EXPIRATION_SECONDS", "600"))

rate_limit_records = defaultdict(list)

def check_rate_limit(ip: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    now = time.time()
    timestamps = rate_limit_records[ip]
    rate_limit_records[ip] = [ts for ts in timestamps if now - ts < window_seconds]
    if len(rate_limit_records[ip]) >= max_requests:
        return False
    rate_limit_records[ip].append(now)
    return True


class PasscodeVerifyRequest(BaseModel):
    passcode: str


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get("/health")
async def health_check():
    """Cloud Run Health Check Probe"""
    return {"status": "ok", "version": "2.0.0", "timestamp": time.time()}


@app.get("/", response_class=HTMLResponse)
async def kiosk_view(request: Request):
    """Main Booth Kiosk Page (Direct Access, No Passcode Gate)"""
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})


@app.post("/api/verify-passcode")
async def verify_passcode(req: PasscodeVerifyRequest):
    """Verify Demo Access Passcode"""
    if not DEMO_PASSCODE or req.passcode.strip() == DEMO_PASSCODE:
        response = JSONResponse({"success": True})
        response.set_cookie(key="demo_authed", value="true", max_age=86400, httponly=True)
        return response
    return JSONResponse({"success": False, "error": "Incorrect security passcode."}, status_code=401)


@app.post("/api/verify-admin-passcode")
async def verify_admin_passcode(req: PasscodeVerifyRequest):
    """Verify Admin Dashboard Access Passcode"""
    if not ADMIN_PASSCODE or req.passcode.strip() == ADMIN_PASSCODE:
        response = JSONResponse({"success": True})
        response.set_cookie(key="admin_authed", value="true", max_age=86400, httponly=True)
        return response
    return JSONResponse({"success": False, "error": "Incorrect admin passcode."}, status_code=401)


@app.get("/api/admin/logout")
async def admin_logout():
    """Logout from Admin Dashboard and revoke admin_authed cookie"""
    response = RedirectResponse(url="/")
    response.delete_cookie(key="admin_authed")
    return response


@app.get("/card/{card_id}", response_class=HTMLResponse)
async def mobile_card_view(request: Request, card_id: str):
    """Mobile Virtual Card Page (Accessed via QR code, strictly expires in 10 mins)"""
    card = card_store.get_card(card_id)
    if not card:
        return HTMLResponse(
            content="<div style='text-align:center; padding: 3rem; color: #fff; font-family: sans-serif; background: #070913; min-height: 100vh;'><h2>⚠️ Card Not Found or Invalid</h2><p>No business card record found for this QR code.</p><a href='/' style='color:#00B2A9;'>Return to Main Page</a></div>",
            status_code=404
        )

    # 10-Minute Security Expiration Check
    if card_store.is_expired(card, timeout_seconds=CARD_EXPIRATION_SECONDS):
        return HTMLResponse(
            content="<div style='text-align:center; padding: 3rem; color: #fff; font-family: sans-serif; background: #070913; min-height: 100vh;'><h2>🔒 Security Expiration Notice (10 Mins)</h2><p style='color: #cbd5e1; margin-top: 1rem;'>For user privacy and data security, this temporary mobile card view has automatically expired and been destroyed.</p><a href='/' style='display:inline-block; margin-top: 1.5rem; padding: 0.8rem 1.5rem; background: linear-gradient(135deg, #00B2A9, #4285F4); color:#fff; text-decoration:none; border-radius:12px; font-weight:700;'>Create New Card 🚀</a></div>",
            status_code=410
        )

    return templates.TemplateResponse(request=request, name="card.html", context={"request": request, "card": card})


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin Dashboard Disabled in V2 - Redirects to Main Page"""
    return RedirectResponse(url="/")


@app.post("/api/generate")
async def api_generate_card(req: CardGenerateRequest, request: Request):
    """Generate Virtual Persona Card & 3D Character Avatar via Gemini AI"""
    try:
        effective_role = req.custom_role.strip() if req.custom_role and req.custom_role.strip() else req.role

        ai_result = generate_persona_and_avatar(
            name=req.name,
            company=req.company,
            role=effective_role,
            lifestyle=req.lifestyle,
            theme=req.theme,
            photo_base64=req.photo_base64,
            email=req.email,
            phone=req.phone
        )

        card_data = {
            "name": req.name,
            "company": req.company,
            "email": req.email,
            "phone": req.phone,
            "role": effective_role,
            "lifestyle": req.lifestyle,
            "theme": req.theme,
            "persona_title": ai_result.get("persona_title"),
            "persona_bio": ai_result.get("persona_bio"),
            "superpowers": ai_result.get("superpowers"),
            "quote": ai_result.get("quote"),
            "avatar_image": ai_result.get("avatar_image"),
            "marketing_consent": req.marketing_consent
        }

        created_card = card_store.create_card(card_data)

        return JSONResponse({
            "success": True,
            "card": created_card,
            "ai_powered": ai_result.get("ai_powered", False)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API ERROR in /api/generate]: {e}", flush=True)
        return JSONResponse({"success": False, "error": f"Card Generation Error: {str(e)}"}, status_code=500)


@app.post("/api/preview-avatar")
async def api_preview_avatar(req: PreviewRequest):
    """Generate a live 3D character preview from webcam photo immediately"""
    try:
        from app.gemini_service import generate_preview_avatar
        avatar_b64 = generate_preview_avatar(req.photo_base64)
        return JSONResponse({"success": True, "avatar_image": avatar_b64})
    except Exception as e:
        print(f"Error generating preview avatar: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/qr/{card_id}")
async def generate_qr_code(card_id: str, request: Request):
    """Generate QR Code Image pointing to /card/{card_id}"""
    forwarded_host = request.headers.get("x-forwarded-host")
    forwarded_proto = request.headers.get("x-forwarded-proto", "https")
    
    if forwarded_host and "0.0.0.0" not in forwarded_host and "127.0.0.1" not in forwarded_host:
        target_url = f"{forwarded_proto}://{forwarded_host}/card/{card_id}"
    else:
        base_url = str(request.base_url).rstrip("/")
        if "0.0.0.0" in base_url or "127.0.0.1" in base_url:
            base_url = os.environ.get("PUBLIC_BASE_URL", str(request.base_url).rstrip("/"))
        target_url = f"{base_url}/card/{card_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=1,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0a1128", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/api/leads/export")
async def export_leads_csv(request: Request):
    """Export captured B2B leads as CSV (Requires Admin Authentication)"""
    if ADMIN_PASSCODE and request.cookies.get("admin_authed") != "true":
        return JSONResponse({"error": "Unauthorized. Admin authentication required."}, status_code=401)

    cards = card_store.list_cards()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Created At", "Name", "Company", "Role", "Email", "Phone", "Persona Title", "Theme", "Marketing Consent"])

    for c in cards:
        writer.writerow([
            c.get("id"),
            c.get("created_at"),
            c.get("name"),
            c.get("company"),
            c.get("role"),
            c.get("email"),
            c.get("phone"),
            c.get("persona_title"),
            c.get("theme"),
            "Yes" if c.get("marketing_consent") else "No"
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=slw_booth_leads_v2.csv"}
    )
