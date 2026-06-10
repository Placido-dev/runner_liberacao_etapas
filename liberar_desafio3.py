import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv('URL')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASS')

ORGANIZATION_ID = 9750

CLUSTERS = [134219, 147049, 147050, 147051]

MODULES = [791387, 791396, 791405]


def authenticate():
    resp = requests.post(
        f"{BASE_URL}/auth/legacy",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("data", {}).get("jwt")
    if not token:
        raise ValueError(f"Token não encontrado: {data}")
    return token


def unlock_module(token: str, cluster_id: int, module_id: int) -> bool:
    resp = requests.patch(
        f"{BASE_URL}/organizations/{ORGANIZATION_ID}/clusters/{cluster_id}/modules/{module_id}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"is_locked": False},
        timeout=15,
    )
    return resp.status_code in (200, 204)


def main():
    print("Autenticando...")
    token = authenticate()
    print(f"Token obtido. Iniciando liberação...\n")

    ok, fail = [], []

    for cluster_id in CLUSTERS:
        for module_id in MODULES:
            success = unlock_module(token, cluster_id, module_id)
            label = f"cluster {cluster_id} | module {module_id}"
            if success:
                ok.append(label)
                print(f"  ✓ Liberado   {label}")
            else:
                fail.append(label)
                print(f"  ✗ Falha      {label}")

    print(f"\nConcluído: {len(ok)} liberados, {len(fail)} falhas.")
    if fail:
        print(f"\nFalhas:\n" + "\n".join(f"  - {f}" for f in fail))


if __name__ == "__main__":
    main()
