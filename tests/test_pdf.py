import asyncio

from auditor.reporting.pdf import generate_pdf


def test_generate_pdf(tmp_path):
    markdown_path = tmp_path / "audit.md"
    pdf_path = tmp_path / "audit.pdf"

    markdown_path.write_text(
        """
# Website Quality Audit

## Executive Summary

| Severity | Findings |
| --- | ---: |
| Critical | 1 |
| High | 2 |
| Medium | 3 |

## Findings

### 1. Missing Alternative Text

**Severity:** MEDIUM

#### Description

The company logo is missing alternative text.

#### Recommendation

Add an accessible name to the logo link.

```html
<a href="/" aria-label="Company homepage">
    <img src="logo.png" alt="">
</a>
""",
        encoding="utf-8",
    )

    result = asyncio.run(
        generate_pdf(
            markdown_path=markdown_path,
            output_path=pdf_path,
        )
    )

    assert result == pdf_path.resolve()
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000

    with pdf_path.open("rb") as f:
        assert f.read(5) == b"%PDF-"