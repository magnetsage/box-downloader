# box.com downloader script

Simple python script that downloads a PDF document hosted on box.com that restricts downloads

## Prerequisits

- Python 3.12.3
- pip

## Requirements

First create a virtual environment and activate it

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
playwright install firefox
```

## Run the script

```bash
.venv/bin/python main.py
```
