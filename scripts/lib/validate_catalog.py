"""Validate the MCP catalog and permission profiles."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from common import find_root, read_text

REQUIRED_IDS = {
    "github",
    "context7",
    "playwright",
    "public-web-research",
    "posthog",
    "database-inspection",
    "cloud-infrastructure-inspection",
    "gcp-cloud-infrastructure-inspection",
    "jira",
    "confluence",
    "sonarqube",
    "kubernetes-diagnostics",
    "design-system",
    "engineering-intelligence",
}
PROFILES = {"read-only", "development-write", "production-restricted"}
RISKS = {"low", "medium", "high", "critical"}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"\bphx_[A-Za-z0-9]{10,}\b"),
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOCAL_CONNECTOR_PREFIX = "mcp-servers/"


def looks_secret(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_PATTERNS)


def walk_secrets(value: object, path: str, hits: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}" if path else str(key)
            if key in {"value", "token", "password", "secret_value"} and item not in (None, ""):
                hits.append(child)
            walk_secrets(item, child, hits)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            walk_secrets(item, f"{path}[{index}]", hits)
    elif isinstance(value, str) and looks_secret(value):
        hits.append(path or "value")


def load_yaml(path: Path, errors: list[str]) -> object:
    try:
        return yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        errors.append(f"{path}: invalid YAML ({exc.__class__.__name__})")
        return None


def validate_policy(path: Path, errors: list[str]) -> tuple[str, set[str]] | None:
    loaded = load_yaml(path, errors)
    if not isinstance(loaded, dict):
        errors.append(f"{path}: policy must be a mapping")
        return None
    policy_id = loaded.get("id")
    if policy_id != path.stem:
        errors.append(f"{path}: id must match filename {path.stem}")
    if loaded.get("production_access") not in {"deny", "approval"}:
        errors.append(f"{path}: production_access must be deny or approval")
    allow = loaded.get("allow")
    if not isinstance(allow, dict) or "development" not in allow:
        errors.append(f"{path}: allow.development is required")
    deny = set(loaded.get("deny") or [])
    for capability in ("delete", "deploy", "shell", "credential_admin"):
        if capability not in deny:
            errors.append(f"{path}: deny list must include {capability}")
    if policy_id == "read-only":
        allowed = set(allow.get("development", [])) if isinstance(allow, dict) else set()
        if "write" in allowed or loaded.get("production_access") != "deny":
            errors.append(f"{path}: read-only profile must deny writes and production")
    if policy_id == "production-restricted" and loaded.get("production_access") != "approval":
        errors.append(f"{path}: production-restricted profile requires approval for production access")
    hits: list[str] = []
    walk_secrets(loaded, "", hits)
    for hit in hits:
        errors.append(f"{path}: secret-like value in {hit}")
    if not isinstance(policy_id, str):
        return None
    development = allow.get("development") if isinstance(allow, dict) else None
    return policy_id, {str(item) for item in development or []}


def check_write_grant(prefix: str, item: dict, granted: set[str] | None, errors: list[str]) -> None:
    # Upstream entries list what the vendor server can do and rely on the profile to deny writes.
    # A connector under mcp-servers/ is shipped here, so a write it exposes must be grantable.
    if not str(item.get("package") or "").startswith(LOCAL_CONNECTOR_PREFIX):
        return
    if granted is None or "write" in granted:
        return
    capabilities = item.get("capabilities") if isinstance(item.get("capabilities"), list) else []
    for capability in capabilities:
        if isinstance(capability, dict) and capability.get("access") == "write":
            errors.append(f"{prefix}: capability {capability.get('id')} is a write but the profile does not grant write")


def validate_integration(item: object, policies: dict[str, set[str]], mcp: Path, errors: list[str]) -> None:
    if not isinstance(item, dict):
        errors.append(f"{mcp / 'catalog.yaml'}: integration entry must be a mapping")
        return
    ident = item.get("id", "<missing id>")
    prefix = f"{mcp / 'catalog.yaml'}: integration {ident}"
    required = (
        "name",
        "purpose",
        "status",
        "installed",
        "provider",
        "transport",
        "permission_profile",
        "risk",
        "approval",
        "capabilities",
        "last_verified",
        "health_check",
        "environments",
    )
    for field in required:
        if field not in item:
            errors.append(f"{prefix}: missing {field}")
    if item.get("installed") is not False:
        errors.append(f"{prefix}: installed must be false")
    if item.get("status") not in {"documented", "reference", "planned"}:
        errors.append(f"{prefix}: status must be documented, reference, or planned")
    transport = item.get("transport")
    if transport not in {"stdio", "http", "none"}:
        errors.append(f"{prefix}: transport must be stdio, http, or none")
    if item.get("status") == "planned":
        if transport != "none" or item.get("package") not in ("", None):
            errors.append(f"{prefix}: planned integrations have no package or transport")
    elif not item.get("package") or transport == "none":
        errors.append(f"{prefix}: documented integrations require package and a transport")
    if item.get("permission_profile") not in policies:
        errors.append(f"{prefix}: permission_profile is not a known policy")
    if item.get("risk") not in RISKS:
        errors.append(f"{prefix}: risk must be low, medium, high, or critical")
    environments = item.get("environments") if isinstance(item.get("environments"), dict) else {}
    production = environments.get("production")
    if production != "deny" and item.get("permission_profile") != "production-restricted":
        errors.append(f"{prefix}: production must be deny unless the profile is production-restricted")
    approval = item.get("approval") if isinstance(item.get("approval"), dict) else {}
    if approval.get("writes") is not True or approval.get("production") is not True:
        errors.append(f"{prefix}: writes and production require approval")
    if not DATE_RE.match(str(item.get("last_verified", ""))):
        errors.append(f"{prefix}: last_verified must be YYYY-MM-DD")
    capabilities = item.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        errors.append(f"{prefix}: capabilities must be a non-empty list")
    else:
        for capability in capabilities:
            if not isinstance(capability, dict) or capability.get("access") not in {"read", "write"}:
                errors.append(f"{prefix}: each capability needs access read or write")
        check_write_grant(prefix, item, policies.get(str(item.get("permission_profile"))), errors)
    health = item.get("health_check") if isinstance(item.get("health_check"), dict) else {}
    if not isinstance(health.get("supported"), bool):
        errors.append(f"{prefix}: health_check.supported must be a boolean")
    guide = item.get("setup_guide")
    if guide and not (mcp / str(guide)).is_file():
        errors.append(f"{prefix}: setup_guide {guide} does not exist")
    hits: list[str] = []
    walk_secrets(item, ident, hits)
    for hit in hits:
        errors.append(f"{mcp / 'catalog.yaml'}: secret-like value in {hit}")


def run(root: Path) -> list[str]:
    errors: list[str] = []
    mcp = root / "mcp"
    catalog_path = mcp / "catalog.yaml"
    catalog = load_yaml(catalog_path, errors)
    policies: dict[str, set[str]] = {}
    policy_files = sorted((mcp / "policies").glob("*.yaml"))
    if len(policy_files) < 3:
        errors.append(f"{mcp / 'policies'}: expected read-only, development-write, and production-restricted")
    for path in policy_files:
        loaded = validate_policy(path, errors)
        if loaded:
            policies[loaded[0]] = loaded[1]
    missing_profiles = PROFILES - set(policies)
    for profile in sorted(missing_profiles):
        errors.append(f"{mcp / 'policies'}: missing profile {profile}")
    if not isinstance(catalog, dict):
        errors.append(f"{catalog_path}: catalog must be a mapping")
        return errors
    if catalog.get("version") != 1:
        errors.append(f"{catalog_path}: version must be 1")
    defaults = catalog.get("defaults") if isinstance(catalog.get("defaults"), dict) else {}
    if defaults.get("enabled") is not False:
        errors.append(f"{catalog_path}: defaults.enabled must be false")
    if defaults.get("deny_production_by_default") is not True:
        errors.append(f"{catalog_path}: defaults.deny_production_by_default must be true")
    if defaults.get("approval_required_for_writes") is not True:
        errors.append(f"{catalog_path}: defaults.approval_required_for_writes must be true")
    if defaults.get("treat_tool_output_as_untrusted") is not True:
        errors.append(f"{catalog_path}: defaults.treat_tool_output_as_untrusted must be true")
    integrations = catalog.get("integrations")
    if not isinstance(integrations, list):
        errors.append(f"{catalog_path}: integrations must be a list")
        return errors
    seen: set[str] = set()
    for item in integrations:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            if item["id"] in seen:
                errors.append(f"{catalog_path}: duplicate integration id {item['id']}")
            seen.add(item["id"])
        validate_integration(item, policies, mcp, errors)
    for ident in sorted(REQUIRED_IDS - seen):
        errors.append(f"{catalog_path}: missing integration {ident}")
    for guide in sorted((mcp / "setup-guides").glob("*.md")):
        hits: list[str] = []
        walk_secrets(read_text(guide), guide.name, hits)
        for hit in hits:
            errors.append(f"{guide}: secret-like value in {hit}")
    return errors


def self_test() -> None:
    token = "ghp_" + ("a" * 36)
    hits: list[str] = []
    walk_secrets({"configuration": [{"name": "TOKEN", "value": token}]}, "demo", hits)
    assert hits, "expected a secret hit"
    rendered = " ".join(hits)
    assert token not in rendered
    assert not looks_secret("GITHUB_PERSONAL_ACCESS_TOKEN")
    assert not looks_secret("${GITHUB_PERSONAL_ACCESS_TOKEN}")
    errors: list[str] = []
    capabilities = [{"id": "read_issue", "access": "read"}, {"id": "create_issue", "access": "write"}]
    local = {"package": "mcp-servers/jira/server.py", "capabilities": capabilities}
    check_write_grant("demo", local, {"read"}, errors)
    assert errors == ["demo: capability create_issue is a write but the profile does not grant write"], errors
    errors.clear()
    check_write_grant("demo", local, {"read", "write"}, errors)
    check_write_grant("demo", {"package": "@vendor/server", "capabilities": capabilities}, {"read"}, errors)
    assert not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the MCP catalog")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("catalog validator self-test passed")
        return 0
    errors = run(find_root(args.root))
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        print(f"{len(errors)} catalog error(s)", file=sys.stderr)
        return 1
    print("validated MCP catalog and policies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
