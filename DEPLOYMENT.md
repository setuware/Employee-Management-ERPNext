# Auto Deployment (GitHub Actions)

Every push to the `main` branch automatically deploys the app to your server:
pull the latest code in `apps/lms`, run `bench migrate` inside the backend
Docker container, and restart the containers.

## How it works

1. You push to `main` on GitHub
2. GitHub Actions connects to your server over SSH
3. `scripts/deploy.sh` runs on the server:
   - `git fetch` + `git reset --hard origin/main` in `apps/lms`
   - `bench --site <site> migrate` inside the backend container
   - `bench --site <site> clear-cache`
   - restarts `frontend`, `backend`, `worker`, `scheduler` containers
   - falls back to running bench directly on the host if no Docker container is found

## One-time setup

### 1. Let the server read the private repo

The server's `apps/lms` checkout must be able to `git fetch` from GitHub.
Easiest: a read-only **deploy key**.

1. On your computer (or the server), generate a key pair:
   ```bash
   ssh-keygen -t ed25519 -f github_deploy_key -N "" -C "lms-server-deploy"
   ```
2. GitHub → repo → **Settings → Deploy keys → Add deploy key**
   - Paste the **public** key (`github_deploy_key.pub`), tick **Allow write access** (needed only if you want the server to push; read access is enough to deploy)
3. On the server, save the **private** key and configure git to use it for this repo:
   ```bash
   mkdir -p ~/.ssh && chmod 700 ~/.ssh
   # paste github_deploy_key content into ~/.ssh/github_deploy_key
   chmod 600 ~/.ssh/github_deploy_key
   git -C /workspace/frappe15-bench/apps/lms remote set-url origin "git@github.com:setuware/Employee-Management-ERPNext.git"
   echo "Host github.com
     User git
     IdentityFile ~/.ssh/github_deploy_key
     StrictHostKeyChecking accept-new" >> ~/.ssh/config
   git -C /workspace/frappe15-bench/apps/lms fetch   # test — should succeed without a password
   ```

> If you prefer, you can instead leave the HTTPS remote and configure a
> credential helper with a personal access token on the server.

### 2. Allow GitHub Actions to SSH into the server

The GitHub workflow connects with its own SSH key.

1. Generate another key pair (private key stays in GitHub; public key goes on the server):
   ```bash
   ssh-keygen -t ed25519 -f actions_deploy_key -N "" -C "github-actions-deploy"
   ```
2. Add the **public** key to the server's `~/.ssh/authorized_keys` (create it if missing):
   ```bash
   mkdir -p ~/.ssh && chmod 700 ~/.ssh
   echo "ssh-ed25519 AAAA... github-actions-deploy" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```
3. Make sure SSH is reachable from the internet (port 22 open). Note: GitHub
   Actions connects from dynamic IP addresses, so you cannot restrict by IP
   unless you use GitHub's `api.github.com/meta` IP ranges.

### 3. Add the GitHub Actions secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret       | Value                                                          |
|--------------|----------------------------------------------------------------|
| `SSH_HOST`   | Server IP or domain (e.g. `203.0.113.10` or `server.setuware.in`) |
| `SSH_PORT`   | SSH port (default `22`)                                        |
| `SSH_USER`   | Server user, e.g. `frappe`                                     |
| `SSH_KEY`    | The **private** key (`actions_deploy_key`) — full content including `-----BEGIN OPENSSH PRIVATE KEY-----` |
| `BENCH_PATH` | Bench path on the server, e.g. `/workspace/frappe15-bench`     |
| `SITE_NAME`  | Site to migrate, e.g. `site1.local` — leave empty to migrate all sites |

## Test it

1. Open the repo on GitHub → **Actions** → **Auto Deploy** → **Run workflow**
   (manual trigger) — no code change needed.
2. Or just push anything to `main` and watch the "Auto Deploy" run.

## Adjusting the deploy steps

Everything that runs on the server lives in `scripts/deploy.sh` — edit it, and
the workflow picks up the changes automatically (it copies the script before
running it). The workflow file itself is `.github/workflows/deploy.yml`.
