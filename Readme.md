# Developing project
## Requirement
- Python (`>=3.10`)
- Poetry

## Working with project
- `git clone https://github.com/arville27/utilcli`
- `cd utilcli`
- `poetry shell`
- `poetry install`

# Configuration file*
## Windows 
* `C:\Users\<user>\AppData\Roaming\utilcli`
## Unix
* `~/.config/utilcli`

## Configuration template
```
{
    "porkbun": {
        "API_KEY": "",
        "SECRET_KEY": "",
        "DOMAIN": "",
        "SERVER_IP": ""
    },
    "shlink": {
        "DOMAIN": "",
        "API_KEY": ""
    },
    "utilapi": {
        "HOST": "",
        "PORT": ""
    }
}

```