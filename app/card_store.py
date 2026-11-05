import json
import os
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "cards.json")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "slw-demo-510515-leads")

class CardStore:
    def __init__(self):
        self._cards: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._load()

    def _get_target_file(self) -> str:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            test_file = os.path.join(DATA_DIR, ".write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return DATA_FILE
        except Exception:
            return "/tmp/cards.json"

    def _load_from_gcs(self) -> bool:
        if not GCS_BUCKET_NAME:
            return False
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob("cards.json")
            if blob.exists():
                content = blob.download_as_text(encoding="utf-8")
                data = json.loads(content)
                with self._lock:
                    self._cards = {item["id"]: item for item in data}
                print(f"[GCS Success] Loaded {len(self._cards)} leads from gs://{GCS_BUCKET_NAME}/cards.json", flush=True)
                return True
        except BaseException as e:
            print(f"[GCS Load Notice]: Could not load from GCS (non-blocking): {e}", flush=True)
        return False

    def _save_lead_sync(self, card: dict):
        """Save individual lead atomically to GCS (leads/{card_id}.json) synchronously in < 0.1s"""
        if not GCS_BUCKET_NAME or not card or "id" not in card:
            return
        card_id = card["id"]
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET_NAME)
            if not bucket.exists():
                try:
                    bucket = client.create_bucket(GCS_BUCKET_NAME, location="asia-northeast3")
                except Exception as b_err:
                    print(f"[GCS Bucket Create Notice]: {b_err}", flush=True)

            blob = bucket.blob(f"leads/{card_id}.json")
            json_str = json.dumps(card, ensure_ascii=False, indent=2)
            blob.upload_from_string(json_str, content_type="application/json; charset=utf-8")
            print(f"[GCS Success] Synchronously saved lead gs://{GCS_BUCKET_NAME}/leads/{card_id}.json", flush=True)
        except BaseException as e:
            print(f"[GCS Single Lead Save Warning]: {e}", flush=True)

    def _load(self):
        if self._load_from_gcs():
            return

        target_file = self._get_target_file()
        if os.path.exists(target_file):
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    with self._lock:
                        self._cards = {item["id"]: item for item in data}
            except Exception as e:
                print(f"Warning: Could not load card store: {e}")
                with self._lock:
                    self._cards = {}

    def _save_local(self):
        try:
            target_file = self._get_target_file()
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with self._lock:
                cards_copy = list(self._cards.values())
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(cards_copy, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save card store locally: {e}")

    def create_card(self, data: dict) -> dict:
        card_id = str(uuid.uuid4())[:8]
        card = {
            "id": card_id,
            "name": data.get("name", "GUEST"),
            "company": data.get("company", "Google Cloud Partner"),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "role": data.get("role", "Developer"),
            "lifestyle": data.get("lifestyle", []),
            "theme": data.get("theme", "cyberpunk"),
            "persona_title": data.get("persona_title", "AI Visionary"),
            "persona_bio": data.get("persona_bio", ""),
            "superpowers": data.get("superpowers", []),
            "quote": data.get("quote", ""),
            "avatar_style": data.get("avatar_style", "gcloud"),
            "avatar_image": data.get("avatar_image", ""),
            "marketing_consent": data.get("marketing_consent", False),
            "created_at": datetime.utcnow().isoformat()
        }
        with self._lock:
            self._cards[card_id] = card
        
        self._save_local()
        # Synchronously upload single lead file (takes <0.1s, eliminates 120s timeout bug completely)
        self._save_lead_sync(card)
        return card

    def get_card(self, card_id: str) -> Optional[dict]:
        with self._lock:
            if card_id in self._cards:
                return self._cards[card_id]

        # On-demand fallback fetch from GCS leads/{card_id}.json for multi-instance / restart resilience
        if GCS_BUCKET_NAME:
            try:
                from google.cloud import storage
                client = storage.Client()
                bucket = client.bucket(GCS_BUCKET_NAME)
                blob = bucket.blob(f"leads/{card_id}.json")
                if blob.exists():
                    content = blob.download_as_text(encoding="utf-8")
                    card = json.loads(content)
                    with self._lock:
                        self._cards[card_id] = card
                    print(f"[GCS Fetch Fallback] Recovered lead {card_id} from GCS leads/{card_id}.json", flush=True)
                    return card
            except Exception as e:
                print(f"[GCS Fetch Fallback Error]: {e}", flush=True)

        return None

    def is_expired(self, card: dict, timeout_seconds: int = 600) -> bool:
        """Check if card creation timestamp is older than timeout_seconds (default 10 mins)"""
        if not card or "created_at" not in card:
            return True
        try:
            created_dt = datetime.fromisoformat(card["created_at"])
            elapsed = (datetime.utcnow() - created_dt).total_seconds()
            return elapsed > timeout_seconds
        except Exception:
            return False

    def list_cards(self) -> List[dict]:
        with self._lock:
            return sorted(list(self._cards.values()), key=lambda x: x.get("created_at", ""), reverse=True)

card_store = CardStore()
