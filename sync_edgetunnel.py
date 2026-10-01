import json
import os
from pathlib import Path
import sys

import requests


def required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def main():
    domain = required_env("EDT_DOMAIN")
    admin_password = required_env("EDT_ADMIN")
    domains = domain.replace("https://", "").replace("http://", "").strip("/")
    hosts_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public/hosts.txt")
    hosts = hosts_path.read_text(encoding="utf-8")
    base_url = f"https://{domains}"

    session = requests.Session()
    login = session.post(
        f"{base_url}/login",
        data={"password": admin_password},
        timeout=60,
    )
    login.raise_for_status()
    if not login.json().get("success"):
        raise RuntimeError("edgetunnel login failed")

    config_response = session.get(f"{base_url}/admin/config.json", timeout=60)
    config_response.raise_for_status()
    config = config_response.json()
    subscription = config.setdefault("优选订阅生成", {})
    local_library = subscription.setdefault("本地IP库", {})

    changed = False
    if subscription.get("local") is not True:
        subscription["local"] = True
        changed = True
    if local_library.get("随机IP") is not False:
        local_library["随机IP"] = False
        changed = True

    if changed:
        config_response = session.post(
            f"{base_url}/admin/config.json",
            json=config,
            timeout=60,
        )
        config_response.raise_for_status()
        if not config_response.json().get("success"):
            raise RuntimeError("edgetunnel config update failed")

    save_response = session.post(
        f"{base_url}/admin/ADD.txt",
        data=hosts.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        timeout=60,
    )
    save_response.raise_for_status()
    if not save_response.json().get("success"):
        raise RuntimeError("edgetunnel node list update failed")

    verify_response = session.get(f"{base_url}/admin/ADD.txt", timeout=60)
    verify_response.raise_for_status()
    if verify_response.text != hosts:
        raise RuntimeError("edgetunnel node list verification failed")

    print(
        "edgetunnel sync ok: "
        f"{len(hosts.encode('utf-8'))} bytes, config_changed={str(changed).lower()}"
    )


if __name__ == "__main__":
    main()
