## ..:: Otomoto scraper ::..


### Features
- Create tables with data scraped from Otomoto search page. Table contains columns as below:

``id, price, production year, engine capacity, fuel type, mileage, brand, model, location, url``


### Prerequisites :coffee:

You will need the following things properly installed on your machine.

* python3
* pip3
```
apt-get install python3-pip
```

### Installation :books:
1. Install all dependencies using 
```
 pip3 install -r requirements.txt 
```


### Run
Try according to line below
```
python3 main.py -url "https://www.otomoto.pl/osobowe/ferrari/" -l ferrari
```