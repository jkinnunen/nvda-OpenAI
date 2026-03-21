import json
import os
import uuid
from .consts import BASE_URLs

AVAILABLE_PROVIDERS = [
	"OpenAI",
	"DeepSeek",
	"CustomOpenAI",
	"Ollama",
	"MistralAI",
	"OpenRouter",
	"Anthropic",
	"xAI",
	"Google",
]

# Common environment variable names per provider (tried in order; first non-empty wins)
_ENV_KEYS = {
	"OpenAI": ("OPENAI_API_KEY", "OPENAI_KEY"),
	"DeepSeek": ("DEEPSEEK_API_KEY",),
	"CustomOpenAI": ("OPENAI_COMPAT_API_KEY", "OPENAI_API_KEY", "OPENAI_KEY"),
	"Ollama": ("OLLAMA_API_KEY",),
	"MistralAI": ("MISTRAL_API_KEY", "MISTRALAI_API_KEY"),
	"OpenRouter": ("OPENROUTER_API_KEY",),
	"Anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_KEY"),
	"xAI": ("XAI_API_KEY", "XAI_KEY"),
	"Google": ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_AI_API_KEY"),
}

_managers = {}
_store_cache_by_dir = {}
_migrated_dirs = set()


def _safe_read_text(path):
	"""Best-effort text read for legacy key files; never raises."""
	try:
		with open(path, "r", encoding="utf-8", errors="replace") as f:
			return f.read().strip()
	except Exception:
		return ""


def _empty_store():
	return {"version": 2, "providers": {}}


def _normalize_account(raw):
	if not isinstance(raw, dict):
		return None
	acc_id = raw.get("id")
	api_key = (raw.get("api_key") or "").strip()
	if not isinstance(acc_id, str):
		return None
	return {
		"id": acc_id,
		"name": (raw.get("name") or "Account").strip() or "Account",
		"api_key": api_key,
		"org_name": (raw.get("org_name") or "").strip(),
		"org_key": (raw.get("org_key") or "").strip(),
		"base_url": (raw.get("base_url") or "").strip(),
	}


def _normalize_provider_bucket(raw_bucket):
	if not isinstance(raw_bucket, dict):
		return {"active_account_id": None, "accounts": []}
	accounts_raw = raw_bucket.get("accounts", [])
	accounts = []
	if isinstance(accounts_raw, list):
		for acc in accounts_raw:
			norm = _normalize_account(acc)
			if norm is not None:
				accounts.append(norm)
	active = raw_bucket.get("active_account_id")
	if not isinstance(active, str):
		active = None
	if active and not any(a["id"] == active for a in accounts):
		active = accounts[0]["id"] if accounts else None
	return {"active_account_id": active, "accounts": accounts}


class APIKeyManager:
	"""Manage API keys/accounts for one provider."""

	def __init__(self, data_dir, provider="OpenAI"):
		if provider not in AVAILABLE_PROVIDERS:
			raise ValueError(f"Unknown provider: {provider}")
		self.data_dir = data_dir
		self.provider = provider
		self.accounts_path = os.path.join(data_dir, "accounts.json")
		self.api_key_path = os.path.join(data_dir, f"{provider}.key")
		self.api_key_org_path = os.path.join(data_dir, f"{provider}_org.key")
		# Some users may have typoed legacy file names; read as fallback only.
		self.api_key_typo_path = os.path.join(data_dir, f"{provider}.kley")
		self.ensure_data_dir()

	def ensure_data_dir(self):
		if not os.path.isdir(self.data_dir):
			os.makedirs(self.data_dir)

	def _get_env_api_key(self, keys):
		"""Return first non-empty value from environment variables."""
		for name in keys:
			val = os.getenv(name)
			if val and val.strip():
				return val.strip()
		return None

	def _normalize_ollama_base_url(self, url):
		"""Normalize Ollama endpoint to OpenAI-compatible /v1 base."""
		raw = (url or "").strip()
		if not raw:
			host = os.getenv("OLLAMA_HOST", "").strip()
			if host:
				raw = host
		if not raw:
			return BASE_URLs.get("Ollama", "http://127.0.0.1:11434/v1")
		if "://" not in raw:
			raw = f"http://{raw}"
		raw = raw.rstrip("/")
		if not raw.lower().endswith("/v1"):
			raw += "/v1"
		return raw

	def _load_shared_store(self):
		if self.data_dir in _store_cache_by_dir:
			return _store_cache_by_dir[self.data_dir]
		store = _empty_store()
		if os.path.isfile(self.accounts_path):
			try:
				with open(self.accounts_path, "r", encoding="utf-8", errors="replace") as f:
					raw = json.load(f)
				if isinstance(raw, dict):
					providers = raw.get("providers")
					if isinstance(providers, dict):
						for provider in AVAILABLE_PROVIDERS:
							store["providers"][provider] = _normalize_provider_bucket(providers.get(provider, {}))
					else:
						# Graceful support for accidental flat shape.
						for provider in AVAILABLE_PROVIDERS:
							store["providers"][provider] = _normalize_provider_bucket(raw.get(provider, {}))
			except Exception:
				store = _empty_store()
		for provider in AVAILABLE_PROVIDERS:
			store["providers"].setdefault(provider, {"active_account_id": None, "accounts": []})
		_store_cache_by_dir[self.data_dir] = store
		return store

	def _save_shared_store(self, store):
		store = store if isinstance(store, dict) else _empty_store()
		store.setdefault("version", 2)
		store.setdefault("providers", {})
		for provider in AVAILABLE_PROVIDERS:
			store["providers"][provider] = _normalize_provider_bucket(store["providers"].get(provider, {}))
		tmp_path = self.accounts_path + ".tmp"
		with open(tmp_path, "w", encoding="utf-8") as f:
			json.dump(store, f)
		os.replace(tmp_path, self.accounts_path)
		_store_cache_by_dir[self.data_dir] = store

	def _provider_bucket(self, store):
		store.setdefault("providers", {})
		if self.provider not in store["providers"]:
			store["providers"][self.provider] = {"active_account_id": None, "accounts": []}
		bucket = store["providers"][self.provider]
		bucket = _normalize_provider_bucket(bucket)
		store["providers"][self.provider] = bucket
		return bucket

	def _migrate_legacy_if_needed(self):
		"""Migrate per-provider JSON and legacy *.key files into accounts.json."""
		if self.data_dir in _migrated_dirs:
			return
		store = self._load_shared_store()
		paths_to_remove = set()
		has_any_accounts = any(
			store["providers"].get(provider, {}).get("accounts")
			for provider in AVAILABLE_PROVIDERS
		)
		changed = False

		# 1) Migrate from previous per-provider files: <provider>_accounts.json
		for provider in AVAILABLE_PROVIDERS:
			pp_path = os.path.join(self.data_dir, f"{provider}_accounts.json")
			if not os.path.isfile(pp_path):
				continue
			try:
				with open(pp_path, "r", encoding="utf-8", errors="replace") as f:
					raw = json.load(f)
				bucket = _normalize_provider_bucket(raw)
				if bucket["accounts"] and not store["providers"][provider]["accounts"]:
					store["providers"][provider] = bucket
					changed = True
					paths_to_remove.add(pp_path)
			except Exception:
				# Ignore invalid per-provider account files.
				pass

		# 2) Migrate from legacy .key/.kley only when provider has no accounts yet.
		for provider in AVAILABLE_PROVIDERS:
			if store["providers"][provider]["accounts"]:
				continue
			key_path = os.path.join(self.data_dir, f"{provider}.key")
			key_typo_path = os.path.join(self.data_dir, f"{provider}.kley")
			org_path = os.path.join(self.data_dir, f"{provider}_org.key")
			legacy_key = _safe_read_text(key_path)
			if not legacy_key:
				legacy_key = _safe_read_text(key_typo_path)
			if not legacy_key:
				continue
			legacy_org = _safe_read_text(org_path)
			org_name = ""
			org_key = ""
			if legacy_org and legacy_org.count(":=") == 1:
				org_name, org_key = legacy_org.split(":=", 1)
			acc_id = uuid.uuid4().hex
			store["providers"][provider] = {
				"active_account_id": acc_id,
				"accounts": [{
					"id": acc_id,
					"name": "Default",
					"api_key": legacy_key,
					"org_name": (org_name or "").strip(),
					"org_key": (org_key or "").strip(),
				}],
			}
			changed = True
			# Remove legacy files only if they were effectively migrated.
			paths_to_remove.add(key_path)
			paths_to_remove.add(key_typo_path)
			if legacy_org:
				paths_to_remove.add(org_path)

		if changed or not has_any_accounts:
			self._save_shared_store(store)
			for old_path in paths_to_remove:
				try:
					if os.path.isfile(old_path):
						os.remove(old_path)
				except Exception:
					# Ignore cleanup failures; migrated data is already saved.
					pass
		_migrated_dirs.add(self.data_dir)

	def list_accounts(self, include_env=False):
		self._migrate_legacy_if_needed()
		store = self._load_shared_store()
		bucket = self._provider_bucket(store)
		accounts = []
		for acc in bucket.get("accounts", []):
			norm = _normalize_account(acc)
			if norm is not None:
				accounts.append(norm)
		if include_env and not accounts and self.provider != "CustomOpenAI":
			env_api = self._get_env_api_key(_ENV_KEYS.get(self.provider, ()))
			if env_api:
				accounts.append({
					"id": "__env__",
					"name": "Environment",
					"api_key": env_api,
					"org_name": "",
					"org_key": "",
				})
		return accounts

	def get_account(self, account_id):
		for acc in self.list_accounts(include_env=True):
			if acc.get("id") == account_id:
				return acc
		return None

	def get_active_account_id(self):
		self._migrate_legacy_if_needed()
		store = self._load_shared_store()
		bucket = self._provider_bucket(store)
		active = bucket.get("active_account_id")
		accounts = self.list_accounts(include_env=True)
		if active and any(a.get("id") == active for a in accounts):
			return active
		return accounts[0]["id"] if accounts else None

	def get_active_account(self):
		active_id = self.get_active_account_id()
		return self.get_account(active_id) if active_id else None

	def set_active_account(self, account_id):
		self._migrate_legacy_if_needed()
		store = self._load_shared_store()
		bucket = self._provider_bucket(store)
		if account_id == "__env__":
			bucket["active_account_id"] = account_id
			self._save_shared_store(store)
			return
		if any(a.get("id") == account_id for a in bucket.get("accounts", [])):
			bucket["active_account_id"] = account_id
			self._save_shared_store(store)

	def add_account(self, name, api_key, org_name="", org_key="", base_url="", set_active=True):
		self._migrate_legacy_if_needed()
		store = self._load_shared_store()
		bucket = self._provider_bucket(store)
		acc_id = uuid.uuid4().hex
		account = {
			"id": acc_id,
			"name": (name or "Account").strip() or "Account",
			"api_key": (api_key or "").strip(),
			"org_name": (org_name or "").strip(),
			"org_key": (org_key or "").strip(),
			"base_url": (base_url or "").strip(),
		}
		if self.provider == "Ollama":
			account["base_url"] = self._normalize_ollama_base_url(account["base_url"])
		if self.provider == "CustomOpenAI":
			if not account["base_url"]:
				raise ValueError("Custom provider URL is required")
		elif self.provider != "Ollama" and not account["api_key"]:
			raise ValueError("API key is required")
		bucket.setdefault("accounts", []).append(account)
		if set_active or not bucket.get("active_account_id"):
			bucket["active_account_id"] = acc_id
		self._save_shared_store(store)
		return acc_id

	def update_account(self, account_id, *, name=None, api_key=None, org_name=None, org_key=None, base_url=None):
		self._migrate_legacy_if_needed()
		store = self._load_shared_store()
		bucket = self._provider_bucket(store)
		updated = False
		for acc in bucket.get("accounts", []):
			if acc.get("id") != account_id:
				continue
			if name is not None:
				acc["name"] = (name or "Account").strip() or "Account"
			if api_key is not None:
				acc["api_key"] = (api_key or "").strip()
			if org_name is not None:
				acc["org_name"] = (org_name or "").strip()
			if org_key is not None:
				acc["org_key"] = (org_key or "").strip()
			if base_url is not None:
				acc["base_url"] = (base_url or "").strip()
			if self.provider == "Ollama":
				acc["base_url"] = self._normalize_ollama_base_url(acc.get("base_url", ""))
			if self.provider == "CustomOpenAI" and not acc.get("base_url", "").strip():
				raise ValueError("Custom provider URL is required")
			updated = True
			break
		if updated:
			self._save_shared_store(store)
		return updated

	def remove_account(self, account_id):
		self._migrate_legacy_if_needed()
		store = self._load_shared_store()
		bucket = self._provider_bucket(store)
		before = len(bucket.get("accounts", []))
		bucket["accounts"] = [a for a in bucket.get("accounts", []) if a.get("id") != account_id]
		after = len(bucket["accounts"])
		if before == after:
			return False
		if bucket.get("active_account_id") == account_id:
			bucket["active_account_id"] = bucket["accounts"][0]["id"] if bucket["accounts"] else None
		self._save_shared_store(store)
		return True

	def get_api_key(self, use_org=False, account_id=None):
		account = self.get_account(account_id) if account_id else self.get_active_account()
		if use_org:
			if account and account.get("org_key"):
				org_name = account.get("org_name") or ""
				return f"{org_name}:={account.get('org_key')}"
			if account_id == "__env__":
				return self._get_env_api_key(("OPEN_AI_ORG_API_KEY",))
			return self._get_env_api_key(("OPEN_AI_ORG_API_KEY",))

		if self.provider == "Ollama":
			if account and account.get("api_key"):
				return account.get("api_key")
			return self._get_env_api_key(_ENV_KEYS.get("Ollama", ()))
		if account and account.get("api_key"):
			return account.get("api_key")
		if account_id == "__env__":
			return self._get_env_api_key(_ENV_KEYS.get(self.provider, ()))
		return self._get_env_api_key(_ENV_KEYS.get(self.provider, ()))

	def get_organization_key(self, account_id=None):
		organization = self.get_api_key(use_org=True, account_id=account_id)
		if not organization or organization.count(":=") != 1:
			return None
		return organization.split(":=", 1)[1]

	def get_organization_name(self, account_id=None):
		organization = self.get_api_key(use_org=True, account_id=account_id)
		if not organization or organization.count(":=") != 1:
			return None
		return organization.split(":=", 1)[0]

	def get_base_url(self, account_id=None):
		account = self.get_account(account_id) if account_id else self.get_active_account()
		if self.provider == "Ollama":
			if not isinstance(account, dict):
				return None
			value = (account.get("base_url") if account else "") if isinstance(account, dict) else ""
			return self._normalize_ollama_base_url(value)
		if account:
			return (account.get("base_url") or "").strip() or None
		return None

	def save_api_key(self, key, org=False, org_name=None, account_id=None):
		# Backward-compatible API: update active account if exists, else create one.
		active = self.get_account(account_id) if account_id else self.get_active_account()
		if active and active.get("id") != "__env__":
			if org:
				self.update_account(active["id"], org_name=(org_name or ""), org_key=(key or ""))
			else:
				self.update_account(active["id"], api_key=(key or ""))
			return
		if not org:
			self.add_account(name="Account", api_key=key, set_active=True)

	def isReady(self, account_id=None):
		if self.provider == "Ollama":
			account = self.get_account(account_id) if account_id else self.get_active_account()
			if not isinstance(account, dict):
				return False
			return bool(self.get_base_url(account_id=account_id))
		if self.provider == "CustomOpenAI":
			base_url = self.get_base_url(account_id=account_id)
			if base_url and base_url.strip():
				return True
			key = self.get_api_key(account_id=account_id)
			return bool(key and key.strip())
		key = self.get_api_key(account_id=account_id)
		return bool(key and key.strip())


def load(data_dir: str):
	"""Initialize API key manager for all providers."""
	global _managers
	for provider in AVAILABLE_PROVIDERS:
		_managers[provider] = APIKeyManager(data_dir, provider)


def get(provider_name: str) -> APIKeyManager:
	"""Get API key manager for provider_name."""
	if provider_name not in AVAILABLE_PROVIDERS:
		raise ValueError(f"Unknown provider: {provider_name}. Available: {AVAILABLE_PROVIDERS}")
	return _managers[provider_name]


def list_configured_accounts(include_env=True):
	"""Return configured accounts across providers."""
	accounts = []
	for provider in AVAILABLE_PROVIDERS:
		manager = get(provider)
		for acc in manager.list_accounts(include_env=include_env):
			accounts.append({
				"provider": provider,
				"id": acc["id"],
				"name": acc["name"],
				"label": f"{provider}/{acc['name']}",
			})
	return accounts
