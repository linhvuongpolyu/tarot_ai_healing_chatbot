# Health Check

Use this quick script to compile `app.py` and catch syntax errors without running Streamlit.

```powershell
python -c "import py_compile; py_compile.compile(r'd:\\MScIME\\SD5913 - Creative Programming for Designers and Artists\\Healing App\\app.py', doraise=True)"
```

If no output appears, compilation succeeded. Then run:

```powershell
streamlit run app.py
```
