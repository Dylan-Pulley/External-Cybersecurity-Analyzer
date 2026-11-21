
# Running Tests

Open PowerShell in the **project root** (where `main.py` is located) with `.venv` activated.

## Run one TLS test file

**Not Yet Valid Certificate Analysis**
```powershell
python -m unittest discover -s tests -p "test_tls_not_yet_valid.py" -v
```

**Self Signed Certificate Analysis**
```powershell
python -m unittest discover -s tests -p "test_tls_self_signed.py" -v
```

**Untrusted Certificate Authority Analysis**
```powershell
python -m unittest discover -s tests -p "test_tls_ca_trust.py" -v
```

## Run one specific test

```powershell
python -m unittest discover -s tests -p "test_tls_ca_trust.py" -k "test_untrusted_ca" -v
```

Change the file name and test name to run another test.

## Run multiple tests

**All top-level tests:**
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

**All port tests** (in the separate `tests/port` folder):
```powershell
python -m unittest discover -s tests/port -p "test_*.py" -v
```

## Read the results

- `OK`: All discovered tests passed.
- `FAILED` or `ERROR`: At least one test failed.
- `Ran 0 tests`: Check the folder, filename, and test name.


