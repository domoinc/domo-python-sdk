# Updating Pypi Instructions

When you make changes to this [GitHub repo](https://github.com/domoinc/domo-python-sdk), you also need to update the [Pypi repository](https://pypi.org/project/pydomo/) with your latest changes.

## Setup

There are some Python packages you will need to install (in a Terminal):

```
python3 -m pip install --upgrade build 
python3 -m pip install --upgrade twine 
```

You will also need a pypi account and access to the package. Domo IT/Ops can provide this for you. Ultimately, you need an API key from Pypi that you will use to upload your latest changes to Pypi. It should begin with `pypi-`.

## Steps to update Pypi

1. Increment the version inside `setup.py`
    1. Double-check this version matches what's already in Pypi
2. Run `python3 -m build` from the `domo-python-sdk` directory
    1. This should create a directory called dist and add two files: `pydomo-{version}-py3-none-any.whl` and `pydomo-{version}.tar.gz`.
3. Run `python3 -m twine upload --repository pypi dist/*`
    1. This will ask for your API key. Paste it in.
    2. You should see that your new version was uploaded successfully.
4. Check Pypi to verify your version was uploaded correctly.
5. Update `CHANGELOG.md` to include your latest changes.

## Sources/More Information

See [Python's docs for this](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

