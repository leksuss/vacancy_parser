# Programming vacancies parser

This is tool for fetching developers salary stats depends on programming languages in Moscow. Script uses [api.hh.ru](https://api.hh.ru/) and [api.superjob.ru](https://api.superjob.ru/) as sources for collect data. Results shown in a table in the terminal. Statistics are collected for the next languages: `JavaScript`, `Java`, `Python`, `Ruby`, `PHP`, `C++`, `C#`, `Go`, `Scala`, `Swift`.

## Requirements

 - python3
 - `environs`
 - `requests`
 - `terminaltables`

## How to install

Get the source code of this repo:
```
git clone https://github.com/leksuss/vacancy_parser.git
```

Go to this script:
```
cd vacancy_parser
```

Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:
```
# If you would like to install dependencies inside virtual environment, you should create it first.
pip3 install -r requirements.txt
```

## How to use

Run script without arguments:
```
python3 parser.py
```

## Example

Here is an example result:

<img width="450" alt="" src="https://user-images.githubusercontent.com/11560975/222732108-b9f30a86-9d8b-4956-a4bb-51c4489b291c.png">


## Project Goals

The code is written for educational purposes on online-course for web-developers dvmn.org.
