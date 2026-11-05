import os
import json
import base64
import time
from typing import Dict, List, Any, Optional

try:
    from google import genai
    from google.genai import types
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False

MEMOJI_REF_PATH = os.path.join(os.path.dirname(__file__), "static", "images", "memoji_3d_avatar.png")

def get_genai_client():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    return genai.Client(api_key=api_key)

def generate_preview_avatar(photo_base64: str) -> str:
    """Generate a live 3D character avatar preview from webcam photo immediately"""
    client = get_genai_client()
    
    prompt = """
    Analyze the facial features (hairstyle, glasses, outfit, expression) of the attached person's photo carefully,
    and generate a stylish, elegant, slim, and friendly 3D Pixar/Memoji style avatar upper-body snapshot for the Google Cloud SLW Global Summit booth.
    Background must have ZERO text or signboards, featuring only pure 3D neon and bokeh lighting effects.
    """
    
    contents = []
    if photo_base64 and "," in photo_base64:
        header, img_str = photo_base64.split(",", 1)
        img_bytes = base64.b64decode(img_str)
        image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
        contents.append(image_part)
    contents.append(prompt)
    
    for attempt in range(1, 3):
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-image',
                contents=contents
            )
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                                mime_type = part.inline_data.mime_type or "image/png"
                                b64_img = base64.b64encode(part.inline_data.data).decode('utf-8')
                                return f"data:{mime_type};base64,{b64_img}"
        except Exception as e:
            print(f"[Preview Avatar Attempt {attempt}/2 Error]: {e}", flush=True)
            time.sleep(1)
    
    return ""

def generate_persona_and_avatar(
    name: str,
    company: str,
    role: str,
    lifestyle: List[str] = None,
    theme: str = "seoul",
    photo_base64: Optional[str] = None,
    email: str = "",
    phone: str = ""
) -> Dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    lifestyle_list = lifestyle or []

    lifestyle_visual_props = []
    for kw in lifestyle_list:
        kw_lower = kw.lower()
        if any(w in kw_lower for w in ["dog", "puppy", "pet", "반려견", "강아지"]):
            lifestyle_visual_props.append("귀여운 3D 강아지를 품에 따뜻하게 안고 있는 포즈")
        elif any(w in kw_lower for w in ["cat", "kitten", "고양이"]):
            lifestyle_visual_props.append("귀여운 3D 고양이를 안고 있는 포즈")
        elif any(w in kw_lower for w in ["coffee", "cafe", "latte", "커피"]):
            lifestyle_visual_props.append("한 손에 세련된 테이크아웃 커피 잔을 들고 있는 포즈")
        elif any(w in kw_lower for w in ["bike", "cycling", "running", "runner", "marathon", "따릉이", "자전거", "러닝"]):
            lifestyle_visual_props.append("멋진 자전거 헬멧이나 트렌디한 러닝화를 착용한 모습")
        elif any(w in kw_lower for w in ["camping", "outdoor", "캠핑"]):
            lifestyle_visual_props.append("감성적인 3D 캠핑 컵이나 아웃도어 소품을 들고 있는 포즈")
        elif any(w in kw_lower for w in ["golf", "골프"]):
            lifestyle_visual_props.append("미니 골프채를 멋지게 들고 있는 포즈")
        elif any(w in kw_lower for w in ["music", "podcast", "audio", "음악"]):
            lifestyle_visual_props.append("귀에 modern 무선 헤드폰을 쓰고 있는 모습")
        elif any(w in kw_lower for w in ["wine", "whiskey", "와인"]):
            lifestyle_visual_props.append("우아한 와인 잔을 들고 있는 포즈")
        elif any(w in kw_lower for w in ["reading", "book", "책"]):
            lifestyle_visual_props.append("감성적인 책을 들고 있는 포즈")
        else:
            lifestyle_visual_props.append(f"'{kw}'를 상징하는 3D 입체 소품을 착용하거나 들고 있는 포즈")

    props_instruction = "\n- ".join(lifestyle_visual_props) if lifestyle_visual_props else "친근하고 환영하는 포즈"

    if lifestyle_list and len(lifestyle_list) > 0:
        lifestyle_str = ", ".join(lifestyle_list)
        keywords_rule_prompt = f"""
       - 🌟 **[키워드 태그 칩 인쇄]**: 명함 하단 영역에 사용자의 라이프스타일 키워드({lifestyle_str})를 3D 입체 뱃지 태그 칩 형태의 깔끔한 그래픽으로 그려주세요.
        """
    else:
        lifestyle_str = "None selected"
        keywords_rule_prompt = """
       - 🛑 [키워드 미선택]: 명함 이미지에 어떠한 키워드 태그 칩이나 글자도 그리지 마세요.
        """

    theme_bg_instructions = {
        "hangang": "🌟 [배경: 여의도 한강공원] 차분한 푸른 한강 물결과 녹지, 여의도 마천루의 3D 실루엣 배경 (글자/간판 절대 금지)",
        "gwanghwamun": "🌟 [배경: 광화문] 우아한 광화문 기와 지붕 곡선과 북악산 실루엣의 3D 배경 (글자/간판 절대 금지)",
        "myeongdong": "🌟 [배경: 명동 & DDP] 동대문디자인플라자(DDP)의 미래지향적 곡선과 은은한 3D 네온 보케 조명 (글자/간판 절대 금지)",
        "seongsu": "🌟 [배경: 성수 붉은벽돌] 빈티지 붉은 벽돌 질감과 세련된 산업 건축 실루엣 (글자/간판 절대 금지)",
        "seoul": "🌟 [배경: SEOUL MY SOUL] 서울 상징 3색(Pink #FF6B9E, Yellow #FFD232, Teal #00B2A9) 네온 오라 아트워크 (글자 절대 금지)",
        "gcloud": "🌟 [배경: Google Cloud] 구글 브랜드 컬러 감성의 입체 3D 구름 조형물 아트워크 (글자 절대 금지)",
        "cyberpunk": "🌟 [배경: 사이버펑크] 화려한 시안/마젠타 홀로그램 조명과 미래 도시 실루엣 (글자 절대 금지)",
        "cosmic": "🌟 [배경: 우주] 신비로운 은하수와 별빛이 빛나는 3D 우주 공간 배경 (글자 절대 금지)",
        "minimal": "🌟 [배경: 미니멀] 골드와 다크 모드의 현대적인 3D 갤러리 건축 공간 (글자 절대 금지)"
    }
    selected_theme_bg = theme_bg_instructions.get(theme, f"'{theme}' 테마에 어울리는 순수 3D 그래픽 배경을 생성해줘.")

    memoji_3d_prompt = f"""
    첨부된 인물의 실제 사진에서 얼굴 특징(헤어스타일, 안경 유무, 의상 스타일, 표정)을 섬세하게 분석하여,
    실제 사람이 아닌 **3D 애플 메모지(Memoji) 및 픽사(Pixar) 3D 애니메이션 캐릭터 스타일의 귀엽고 트렌디한 3D 캐릭터 상반신 아바타**가 중앙에 선명하게 들어간 프리미엄 세로형 명함 이미지(54mm x 86mm 비율)를 생성해줘.

    🚨🚨🚨 [핵심 스타일 규칙: 실제 사진 금지 / 3D 캐릭터 전용]:
    - 🛑 **절대로 실제 사람 사진을 그대로 출력하지 마세요.**
    - 🌟 **반드시 입체감 있고 세련된 3D Pixar / Memoji 스타일의 3D 아바타 캐릭터로 변환하여 그려주세요.**

    🚨🚨🚨 [배경 텍스트 절대 금지 규칙]:
    - 🛑 **명함 배경이나 주변 건물, 길거리, 간판에 알 수 없는 영문, 한글, 가짜 글자가 절대로 생성되지 않도록 해줘.**
    - 🛑 **배경은 오직 3D 건축물의 실루엣, 랜드마크 구조물, 은은한 네온 조명 효과와 보케(Bokeh) 효과로만 100% 구성해줘.**

    🚨🚨🚨 [명함 인쇄 텍스트 규칙: 영문으로 출력]:
    - 🛑 **명함 이미지 상단 및 하단에 들어가는 인적사항 텍스트는 오직 아래 5가지 사용자 영문 정보만 선명한 Latin 폰트로 인쇄해줘:**
    - [Name]: "{name}"
    - [Company]: "{company}"
    - [Role]: "{role}"
    - [Email]: "{email.strip() if email else 'N/A'}"
    - [Phone]: "{phone.strip() if phone else 'N/A'}"

    [테마 배경 규칙]: {selected_theme_bg}
    - {keywords_rule_prompt}
    """

    client = genai.Client(api_key=api_key)

    # 1. Generate Persona Text via gemini-3.5-flash in ENGLISH
    persona_title = f"Global {role} & {lifestyle_list[0] if lifestyle_list else 'Visionary'}"
    persona_bio = f"{name} is an impactful {role} at {company}, blending professional excellence with a passion for {lifestyle_str}."
    superpowers = [f"✨ {role}"] + [f"🌟 {kw}" for kw in lifestyle_list[:2]]
    quote = "Shaping the future of global smart city innovation together."

    text_prompt = f"""
    You are the AI Digital Business Card Service at the Seoul Smart City x Google Cloud Smart Life Week (SLW) Global Summit.
    Visitor Info:
    - Name: {name}, Company: {company}, Role: {role}, Lifestyle/Interests: [{lifestyle_str}]
    
    You MUST respond STRICTLY in JSON format in ENGLISH:
    {{
        "persona_title": "Witty and inspiring English persona title (e.g. AI Visionary & Smart City Pioneer)",
        "persona_bio": "An engaging 2-sentence professional bio in ENGLISH highlighting their role at {company} and passion for {lifestyle_str}.",
        "superpowers": ["Skill Badge 1", "Skill Badge 2"],
        "quote": "An inspiring one-line vision quote in ENGLISH"
    }}
    """

    for t_attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[text_prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            if response.text:
                p_info = json.loads(response.text)
                persona_title = p_info.get("persona_title", persona_title)
                persona_bio = p_info.get("persona_bio", persona_bio)
                superpowers = p_info.get("superpowers", superpowers)
                quote = p_info.get("quote", quote)
                print(f"[Gemini 3.5 Flash English Persona Generated (Attempt {t_attempt})]", flush=True)
                break
        except Exception as tex_err:
            print(f"[Gemini 3.5 Flash Text Generation Attempt {t_attempt}/3 Failed]: {tex_err}", flush=True)
            time.sleep(1)

    # 2. Generate Image via gemini-3.1-flash-image or gemini-2.5-flash-image
    contents_payload = []
    if photo_base64 and "," in photo_base64:
        try:
            header, img_str = photo_base64.split(",", 1)
            img_bytes = base64.b64decode(img_str)
            image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            contents_payload.append(image_part)
        except Exception as img_p_err:
            print(f"[Photo payload decode warning]: {img_p_err}", flush=True)

    logo_path = os.path.join(os.path.dirname(__file__), "static", "images", "seoul_my_soul_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_bytes = f.read()
            logo_part = types.Part.from_bytes(data=logo_bytes, mime_type="image/png")
            contents_payload.append(logo_part)

    gemini_logo_path = os.path.join(os.path.dirname(__file__), "static", "images", "gemini_star_logo.png")
    if os.path.exists(gemini_logo_path):
        with open(gemini_logo_path, "rb") as f:
            gemini_bytes = f.read()
            gemini_part = types.Part.from_bytes(data=gemini_bytes, mime_type="image/png")
            contents_payload.append(gemini_part)

    contents_payload.append(memoji_3d_prompt)

    avatar_b64 = ""
    last_img_error = None

    image_models_to_try = ['gemini-3.1-flash-image', 'gemini-2.5-flash-image']

    for img_model in image_models_to_try:
        try:
            print(f"[Calling Image Model {img_model}...]", flush=True)
            img_response = client.models.generate_content(
                model=img_model,
                contents=contents_payload
            )

            if img_response.candidates:
                for candidate in img_response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                                mime_type = part.inline_data.mime_type or "image/png"
                                b64_img = base64.b64encode(part.inline_data.data).decode('utf-8')
                                avatar_b64 = f"data:{mime_type};base64,{b64_img}"
                                print(f"[{img_model} Image Generated Successfully!]", flush=True)
                                break
                    if avatar_b64:
                        break

            if avatar_b64:
                break

        except Exception as img_err:
            last_img_error = img_err
            print(f"[{img_model} Image Model Failed/Quota]: {img_err}", flush=True)

    return {
        "persona_title": persona_title,
        "persona_bio": persona_bio,
        "superpowers": superpowers,
        "quote": quote,
        "avatar_image": avatar_b64,
        "ai_powered": True
    }
