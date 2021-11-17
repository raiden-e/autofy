import json

import config
from github import Github, InputFileContent

gist_id = config.GIST['ID']
token = config.GIST['TOKEN']

gist = Github(token).get_gist(gist_id)


def load(gist_name):
    x = gist.files[gist_name].content
    return json.loads(x)


def update(filename: str, content, description: str):
    if not isinstance(filename, str):
        raise ValueError("playlist_name has to be specified")
    if not isinstance(content, str):
        raise ValueError("input has to be specified")

    gist.edit(
        description=description,
        files={f'{filename}': InputFileContent(json.dumps(content, indent=2))})
