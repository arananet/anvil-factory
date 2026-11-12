#!/usr/bin/env python3
"""Deploy a directory to GitHub Pages by committing it to the pages branch.

Usage:
  deploy_github_pages.py <dir>                  production: the site root
  deploy_github_pages.py <dir> --preview NAME   a preview under previews/NAME/
  deploy_github_pages.py --cleanup NAME         remove previews/NAME/

Options: --branch gh-pages  --remote origin (a remote name or a URL)

Production replaces the site root and keeps previews/, CNAME and .nojekyll.
Previews live beside it, so one Pages site serves the product and every
work order's preview: https://<owner>.github.io/<repo>/previews/<NAME>/.

The push uses the checkout's own credentials. When GH_TOKEN or GITHUB_TOKEN
is set and the remote is https://github.com, the token is handed to git
through its environment, never through a URL or an argument.
"""

import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KEEP_AT_ROOT = {".git", "previews", "CNAME", ".nojekyll"}


def git(args, cwd, env, check=True):
    proc = subprocess.run(["git"] + args, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=300)
    if check and proc.returncode != 0:
        raise SystemExit(f"git {args[0]} failed: {(proc.stderr or proc.stdout).strip()[:400]}")
    return proc


def git_env(remote_url):
    env = dict(os.environ)
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token and remote_url.startswith("https://github.com/"):
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                    "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {basic}"})
    return env


def copy_tree(source, target):
    for item in Path(source).iterdir():
        if item.name == ".git":
            continue
        dest = Path(target) / item.name
        if item.is_dir():
            shutil.copytree(item, dest, symlinks=False)
        else:
            shutil.copy2(item, dest)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="deploy_github_pages")
    parser.add_argument("directory", nargs="?")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--preview")
    group.add_argument("--cleanup")
    parser.add_argument("--branch", default="gh-pages")
    parser.add_argument("--remote", default="origin")
    args = parser.parse_args(argv)
    name = args.preview or args.cleanup
    if name and not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", name):
        raise SystemExit("preview name must be lowercase letters, digits and hyphens")
    if not args.cleanup:
        if not args.directory or not Path(args.directory).is_dir():
            raise SystemExit("a directory to deploy is required")
    remote = args.remote
    if "://" not in remote and not Path(remote).exists():
        remote = git(["remote", "get-url", remote], Path.cwd(), dict(os.environ)).stdout.strip()
    env = git_env(remote)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "pages"
        work.mkdir()
        git(["init", "-q"], work, env)
        fetched = git(["fetch", "-q", "--depth", "1", remote, args.branch], work, env, check=False).returncode == 0
        if fetched:
            git(["checkout", "-q", "-B", args.branch, "FETCH_HEAD"], work, env)
        else:
            git(["checkout", "-q", "--orphan", args.branch], work, env)
        if args.cleanup:
            target = work / "previews" / name
            if not target.exists():
                print(f"No preview {name} on {args.branch}; nothing to remove.")
                return 0
            shutil.rmtree(target)
            message = f"Remove preview {name}"
        elif args.preview:
            target = work / "previews" / name
            if target.exists():
                shutil.rmtree(target)
            target.mkdir(parents=True)
            copy_tree(args.directory, target)
            message = f"Deploy preview {name}"
        else:
            for item in work.iterdir():
                if item.name not in KEEP_AT_ROOT:
                    shutil.rmtree(item) if item.is_dir() else item.unlink()
            copy_tree(args.directory, work)
            message = "Deploy site"
        (work / ".nojekyll").touch()
        git(["add", "-A"], work, env)
        if git(["diff", "--cached", "--quiet"], work, env, check=False).returncode == 0:
            print("Nothing changed; the pages branch is already up to date.")
            return 0
        git(["-c", "user.name=anvil", "-c", "user.email=anvil@localhost", "commit", "-q", "-m", message], work, env)
        git(["push", "-q", remote, f"HEAD:refs/heads/{args.branch}"], work, env)
    print(f"{message}: pushed to {args.branch}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
