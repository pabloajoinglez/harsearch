# harsearch (HAR Search Tool)

A command line tool for searching through HAR files 

## Installation

```bash
pip install harsearch
```

## Features

- Search requests/responses/headers/URLs
- Regex support
- Colored output
- Configurable context
- Cross-platform support (Windows/macOS/Linux)

## Usage

```bash
harsearch HAR_FILE PATTERN [OPTIONS]
```
## Options

| Option          | Description                          |
|-----------------|--------------------------------------|
| `-r`, `--regex` | Use regular expression pattern       |
| `-req`          | Search in request fields            |
| `-res`          | Search in response fields           |
| `-url`          | Search in URLs (request only)       |
| `-headers`      | Search in headers                   |
| `-text`         | Search in content text              |
| `-n NUM`        | Context characters (default: 50)    |

## Examples

1. Search domain in URLs:
```bash
harsearch log.har "example.com" -req -url
```

2. Regex search in headers:
```bash
harsearch log.har -r "content-type:.*json" -res -headers
```

3. Find API keys:
```bash
harsearch log.har -r "api_key=[A-Za-z0-9]{32}" -res -text -n 20
```

## License

MIT License
