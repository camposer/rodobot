# rodobot

Simple trading bot using the Binance API

## Setup

### Pre setup
```
brew install ta-lib
```

For M1 Processors, check the following [post](https://stackoverflow.com/a/67045629/3090309).

### Configure venv
```
conda create --prefix venv
conda install --prefix venv pip
conda activate venv/
pip install -r requirements/dev.txt
```

## Run Tests

### Locally
```
pytest
```

### Using Docker
```
docker build -t rodobot .
docker run --rm -it rodobot pytest
```

