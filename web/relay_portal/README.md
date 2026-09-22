# Relay Portal Demo

This is a minimal static demo of the Relay incident portal UI.

How to run locally:

```
cd web/relay_portal
# serve with a simple static server
python3 -m http.server 8000
# then open http://localhost:8000 in your browser
```

Options:
- To point the demo at a live API, append an `api` query parameter or set `window.API_ENDPOINT` in `index.html`. Example:

http://localhost:8000/?api=https://your-api.execute-api.us-east-1.amazonaws.com
