# envault

> A simple secrets manager that syncs `.env` files securely across dev environments using encrypted storage backends.

---

## Installation

```bash
pip install envault
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add envault
```

---

## Usage

**Push your local `.env` to encrypted storage:**

```bash
envault push --env .env --project myapp
```

**Pull secrets to a new machine:**

```bash
envault pull --project myapp --out .env
```

**Use in code:**

```python
from envault import load

load(project="myapp")  # Decrypts and injects secrets into os.environ
```

Envault supports multiple storage backends out of the box:

| Backend | Flag |
|---------|------|
| Local (default) | `--backend local` |
| AWS S3 | `--backend s3` |
| HashiCorp Vault | `--backend vault` |

Secrets are encrypted with AES-256 before leaving your machine. Your encryption key is never stored remotely.

---

## Configuration

Create an `envault.toml` in your project root to set defaults:

```toml
[envault]
project = "myapp"
backend = "s3"
bucket  = "my-secrets-bucket"
```

---

## License

MIT © [envault contributors](https://github.com/yourname/envault)