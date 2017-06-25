#!/usr/bin/env python3
import importParentDir
from config import local_config


if __name__ == '__main__':
    print(dir(local_config))
    print(local_config.projectDir)
    print(local_config.dataLocation)
