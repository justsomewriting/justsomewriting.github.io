## You really shouldn't use this tool

The reason is the tool itself is very deeply tied to the way I name and number the files. The interface is not good for you if you don't use my naming system.

But if you really want to, keep in mind to execute

```
cd tooling
python conversion.py
```

The point is CWD must be /tooling. If it's not, the output file appears in weird places. Also, make sure you install requirements.txt using

```
pip install -r requirements.txt
```

In the UI, all fields are mandatory unless stated otherwise.