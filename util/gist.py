import json

import json5
import config
from github import Github, InputFileContent

gist_id = config.GIST['ID']
token = config.GIST['TOKEN']

gist = Github(token).get_gist(gist_id)


def _fix_surrogates(obj):
    # Fixes escaped UTF-16 surrogate pairs, like emojis
    if isinstance(obj, str):
        return obj.encode("utf-16", "surrogatepass").decode("utf-16")
    if isinstance(obj, dict):
        return {_fix_surrogates(k): _fix_surrogates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fix_surrogates(v) for v in obj]
    return obj


def load(gist_name):
    x = gist.files[gist_name].content
    return _fix_surrogates(json5.loads(x))


def update(filename: str, content, description: str):
    if not isinstance(filename, str):
        raise ValueError("playlist_name has to be specified")

    gist.edit(
        description=description,
        files={f'{filename}': InputFileContent(json.dumps(content, indent=2))})
