# tab-export

> Browser extension companion CLI that processes exported browser tab lists into organized markdown or Notion-ready format.

---

## Installation

```bash
pip install tab-export
```

Or install from source:

```bash
git clone https://github.com/yourusername/tab-export.git && cd tab-export && pip install .
```

---

## Usage

Export your tabs from the browser extension, then run:

```bash
tab-export input.json --format markdown --output tabs.md
```

**Export to Notion-ready format:**

```bash
tab-export input.json --format notion --output notion_tabs.md
```

**Options:**

| Flag | Description |
|------|-------------|
| `--format` | Output format: `markdown` or `notion` (default: `markdown`) |
| `--output` | Output file path (default: stdout) |
| `--group-by` | Group tabs by `domain` or `date` |

**Example output:**

```markdown
## github.com
- [awesome-project](https://github.com/user/awesome-project)
- [another-repo](https://github.com/user/another-repo)

## news.ycombinator.com
- [Show HN: Something cool](https://news.ycombinator.com/item?id=12345)
```

---

## Requirements

- Python 3.8+
- Compatible browser extension *(link coming soon)*

---

## License

MIT © 2024