"""TeX environment validation without external compilation."""

import pytest

from pdl.author.util.tex import TeXConfig


def test_unsupported_engine_is_explicit() -> None:
    with pytest.raises(ValueError, match="only"):
        TeXConfig(engine="katex")
