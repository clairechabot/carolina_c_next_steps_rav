"""Apply a client bundle from clients/<name>/ over this repository.

One repo per client, one template upstream (onboarding/12-multi-client.md).
A client bundle mirrors the repo layout for the files that differ per
client:

    clients/<name>/client/config.py
    clients/<name>/profile/candidate.md
    clients/<name>/claude-project/instructions.md
    clients/<name>/claude-project/knowledge/*.md

Run this ONCE in the client's freshly created repo:

    python tools/apply_client.py <name>

It copies the bundle over the working tree, then removes the whole
clients/ directory (the client repo must not carry other clients' data).
Commit the result. The template repo keeps clients/ as the operator's
staging area.

Refuses to run if the bundle would overwrite a file it does not own, and
never touches secrets: salary floors and contact details stay in the
CANDIDATE_PROFILE secret and the private Claude Project.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_PREFIXES = ("client/", "profile/", "claude-project/")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python tools/apply_client.py <client-name>")
    name = sys.argv[1]
    bundle = ROOT / "clients" / name
    if not bundle.is_dir():
        sys.exit(f"no bundle at {bundle}")

    files = [p for p in bundle.rglob("*") if p.is_file()
             and p.name != "README.md" and "__pycache__" not in p.parts]
    for src in files:
        rel = src.relative_to(bundle).as_posix()
        if not rel.startswith(ALLOWED_PREFIXES):
            sys.exit(f"refusing: {rel} is outside the client-owned paths "
                     f"{ALLOWED_PREFIXES}")
    for src in files:
        rel = src.relative_to(bundle)
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"  {rel}")
    shutil.rmtree(ROOT / "clients")
    print(f"applied {len(files)} file(s) from clients/{name}; removed clients/")
    print("Next: commit, then fill the secrets/variables from the bundle's "
          "README.")


if __name__ == "__main__":
    main()
