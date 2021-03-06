# Blogify

## Introduction
this is Maktab53 Python-Django boot camp first project

## Instructor
* Mr Farzanmehr
## Team members
* Pooria Assarehsa
* Hamidreza Mohammadi
* Sina Esmaili
* Seyed Sina Sadeghesfahani

## install project

First things first, you need to install the project properly and the following structure will provide you an easy installation experience that needs no prior background knowledge

1. install the project with powerful python install packages tool pip.
`< pip install -e .>`  or `< py -m pip install -e .>` or `< python -m pip install -e .>`
2. create virtual environment to isolate your project with following steps 

windows | linux
--------|----------
mkdir myproject | $ mkdir myproject
cd myproject | $ cd myproject
py -3 -m venv venv | $ python3 -m venv venv
venv\Scripts\activate | venv/bin/activate

4. install flask into your environment by `< pip install flask>` or `< py pip install flask>` or `< python pip install flask>`
5. set variables needed to start project with flask

windows | linux
--------|----------
set FLASK_APP=blog | export FLASK_APP=blog
set FLASK_ENV=development | export FLASK_ENV=development
flask run | flask run

## Project road map

### - [x] phase 1 (deadline: 22th Mordad)
* github repository
* database design
* index page
* authentication
 
Task | in charge
-----|----------
index (front) | Sadeghesfahani 
index (back)  | Assarehha 
authentication (front) | Mohammadi 
authentication (back) | Esmaili 

### deligation completed status:
- [x] Sadeghesfahani
- [x] Esmaili
- [ ] Assareha
- [ ] Mohammadi

### - [ ] phase 2 (deadline: 29th Mordad)
* create and edit posts
* unpublish and delete posts
* category view
* user panel

Task | in charge
-----|----------
create (front) | sadeghesfahani [x]
category (front), create (back)  | Assarehha
category, user (back) | Mohammadi
user (front) | Esmaili

### - [ ] phase 3 (deadline: 5th Shahrivar)
* like and dislike
* search engine
* debug
