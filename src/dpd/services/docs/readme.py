from dpd.models import Config
from directory_tree import DisplayTree


class ReadmeService:
    @staticmethod
    def generate_file(conf: Config):
        text =  f"""
# Data Platform Deployer

This is a CLI tool to deploy a data platform using Docker Compose.

### Directory Structure:
```
{DisplayTree(conf.project.name, stringRep=True, showHidden=True)}```
"""
        with open(f"{conf.project.name}/README.md", "w") as f:
            f.write(text)
        return text
