import os
from fabric.api import local, lcd


def clean():
    with lcd(os.path.dirname(__file__)):
        local('python3.6 setup.py clean --all')


def make():
    local("python3.6 setup.py bdist_wheel")
