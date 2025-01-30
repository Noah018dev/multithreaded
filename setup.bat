:: remove if you've already installed
:: should work for .sh just remove these comments... also replace python with python3!
:: pip install twine wheel setuptools
python setup.py bdist_wheel
python -m twine upload --repository pypi dist/* --verbose