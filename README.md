# Blogify

## Introduction
this is Maktab52 Python-Django boot camp first project
## Team members
* pooria asareha
* hamidreza mohammadi
* sina esmaili
* seyed sina sadeghesfahani

## install project

first thing first, you need to install the project properly and the following structure will provide you an easy install experience need no prior background knowledge

1. install the project with powerfull python install packages tool pip.
`< pip install -e .>`  or `< py -m pip install -e .>` or `< python -m pip install -e .>`
2. create virtual environment to isolate your project with following steps 

windows | linux
--------|----------
mkdir myproject | $ mkdir myproject
cd myproject | $ cd myproject
py -3 -m venv venv | $ python3 -m venv venv
venv\Scripts\activate | venv/bin/activate

4. install flask into your environment by `< pip install flask>` or `< py pip install flask>` or `< python pip install flask>`
4. set variables needed to start project with flask
windows | linux
--------|----------
set FLASK_APP=blog | export FLASK_APP=blog
set FLASK_ENV=development | export FLASK_ENV=development
flask run | flask run
