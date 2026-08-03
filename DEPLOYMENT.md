# Auto Deployment (GitHub Actions)

Every push to the `main` branch automatically deploys the app to your server:
pull the latest code in `apps/lms`, run `bench migrate` inside the Docker
container, and clear caches.

## Server topology (current)

- One Docker container runs the whole bench: `/workspace/frappe15-bench`
  (Frappe 15, dev server on port 8000). Find its ID with `docker ps`.
- The bench path does **not** exist on the host — everything runs inside the
  container as user `frappe`.
- `scripts/deploy.sh` detects this automatically:
  - if `$BENCH_PATH/apps` exists on the host → runs directly
  - otherwise → finds the bench container (`docker ps -qf "name=<pattern>"`,
    falling back to names `bench`, `frappe`, `backend`, `web`, `worker`) and
    runs the deploy **inside** it via `docker cp` + `docker exec`

## How it works

1. You push to `main` on GitHub
2. GitHub Actions connects to your server over SSH
3. `scripts/deploy.sh` runs:
   - `git fetch` + `git reset --hard origin/main` in `apps/lms`
   - `bench --site <site> migrate` inside the container
   - `bench --site <site> clear-cache` / `clear-website-cache`

## One-time setup

### 1. Let the server read the private repo

The container's git (running as `frappe`) must be able to fetch from GitHub.
Use a read-only **deploy key** and put it **inside the container**.

1. Generate a key pair on the server host:
   ```bash
   ssh-keygen -t ed25519 -f github_deploy_key -N "" -C "lms-server-deploy"
   ```
2. GitHub → repo → **Settings → Deploy keys → Add deploy key**
   - Paste the **public** key (`github_deploy_key.pub`), read access is enough
3. Copy the key into the container and tell git to use it:
   ```bash
   CONTAINER=$(docker ps -qf name=bench | head -1)   # or your container name
   docker cp ~/.ssh/github_deploy_key $CONTAINER:/home/frappe/.ssh/github_deploy_key
   docker exec $CONTAINER bash -c "chown frappe:frappe /home/frappe/.ssh/github_deploy_key && chmod 600 /home/frappe/.ssh/github_deploy_key"
   docker exec $CONTAINER bash -c "echo 'Host github.com
     User git
     IdentityFile /home/frappe/.ssh/github_deploy_key
     StrictHostKeyChecking accept-new' > /home/frappe/.ssh/config && chown frappe:frappe /home/frappe/.ssh/config"
   docker exec -u frappe $CONTAINER ssh -T git@github.com   # test: should say "Hi setuware/Employee-Management-ERPNext!"
   ```
4. Clone the app (folder name **must** be `lms`):
   ```bash
   docker exec -u frappe $CONTAINER bash -c "cd /workspace/frappe15-bench/apps && git clone git@github.com:setuware/Employee-Management-ERPNext.git lms"
   ```

### 2. Allow GitHub Actions to SSH into the server

The workflow connects with its own SSH key to the **host** user (`ubuntu`).

1. Generate a key pair (private key goes to GitHub; public key on the server):
   ```bash
   ssh-keygen -t ed25519 -f actions_deploy_key -N "" -C "github-actions-deploy"
   ```
2. Add the **public** key to the host's `~/.ssh/authorized_keys`
3. Make sure SSH port 22 is reachable from the internet

### 3. Add the GitHub Actions secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret              | Value                                            |
|---------------------|--------------------------------------------------|
| `SSH_HOST`          | Server IP or domain                              |
| `SSH_PORT`          | SSH port (default `22`)                          |
| `SSH_USER`          | Host user, e.g. `ubuntu` (NOT `frappe`)          |
| `SSH_KEY`           | Private `actions_deploy_key` (full content)      |
| `BENCH_PATH`        | `/workspace/frappe15-bench`                      |
| `SITE_NAME`         | `erp.setuware.in`                                |
| `CONTAINER_PATTERN` | Container name/pattern if it's not `bench`/`frappe`/`backend` (optional) |

## Test it

1. Repo → **Actions** → **Auto Deploy** → **Run workflow** (manual trigger), or
2. Push anything to `main`.

## Adjusting the deploy steps

Everything that runs on the server lives in `scripts/deploy.sh` — the workflow
copies it before running, so edits are picked up automatically. The workflow
file itself is `.github/workflows/deploy.yml`.
