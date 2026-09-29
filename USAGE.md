# json_to_markdown.py — usage

One dependency-free Python 3 file. Stdlib only (`json`, `sys`) — no pip
installs, no network calls, no shell execution. The input file is
opened read-only and is never modified.

## Run

```
python3 json_to_markdown.py <input.json>
```

- Prints a Markdown table to **stdout** and exits `0` on success.
- On any validation failure, prints nothing to stdout, prints one
  `error: ...` line per problem to **stderr**, and exits `1`.
- Wrong number of arguments exits `2` with a usage line on stderr.

## Input shape

A JSON array of records, each requiring:

| field | type | notes |
|---|---|---|
| `id` | string | non-empty, must be unique across the file |
| `title` | string | |
| `description` | string | |
| `rewardAtoms` | integer | canonical JSON integer, non-negative, not a string or float |
| `status` | string | |

## Output

A Markdown table with columns **Title, Description, Job ID, Reward,
Status**, one row per input record in input order. `rewardAtoms` is
rendered as USDC with exactly six decimal places (atoms ÷ 1,000,000).
Pipes, newlines, and angle brackets in any text field are escaped to
literal characters (`\|`, `\n`, `&lt;`/`&gt;`) so they display as text
instead of breaking the table or injecting raw HTML.

## Validation (any failure → exit 1, no output)

- missing required field on any record
- duplicate `id` across records
- `rewardAtoms` that isn't a canonical non-negative JSON integer
  (a quoted number, a float, or a negative number all fail)

## Example

```
$ python3 json_to_markdown.py fixtures/json-to-markdown.input.json
| Title | Description | Job ID | Reward | Status |
| --- | --- | --- | --- | --- |
| ... | ... | job-001 | 2.500000 USDC | open |
```

See `demo/json-to-markdown.output.md` for the full rendered output and
`demo/transcript.txt` for a real run against the valid fixture and all
three invalid fixtures under `fixtures/`.
