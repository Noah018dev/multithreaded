python3 -m pip install twine wheel setuptools
python3 ./setup.py bdist_wheel
python3 -m twine upload --repository pypi dist/* --verbose