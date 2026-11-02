"""Build independent English and Chinese documentation with shared examples."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "_build" / "html"
LANDING_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>pdl — Documentation / 文档</title>
  <style>
    body { font: 1.1rem/1.7 system-ui, sans-serif; max-width: 36rem;
           margin: 12vh auto; padding: 0 1.5rem; }
    a { color: #175cb0; }
  </style>
</head>
<body>
  <h1>pdl</h1>
  <p>Choose a language / <span lang="zh-CN">选择语言</span></p>
  <ul>
    <li><a href="en/index.html" lang="en" hreflang="en">English</a></li>
    <li><a href="zh/index_zh.html" lang="zh-CN" hreflang="zh-CN">中文</a></li>
  </ul>
</body>
</html>
"""


def main() -> None:
    """Build both sites, generating the shared example outputs only once."""
    for locale in ("en", "zh"):
        environment = os.environ.copy()
        environment["PDL_DOCS_LANGUAGE"] = locale
        environment["PDL_DOCS_SKIP_EXAMPLES"] = "1" if locale == "zh" else "0"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-W",
                "--keep-going",
                "-b",
                "html",
                "docs",
                str(OUTPUT / locale),
            ],
            cwd=ROOT,
            env=environment,
            check=True,
        )
    if (OUTPUT / ".buildinfo").exists():
        # Retire the previous mixed-language site's generated files after success.
        for path in OUTPUT.iterdir():
            if path.name in {"en", "zh", "index.html"}:
                continue
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
    (OUTPUT / "index.html").write_text(LANDING_PAGE, encoding="utf-8")
    print(f"Documentation ready: {OUTPUT / 'index.html'}")


if __name__ == "__main__":
    main()
