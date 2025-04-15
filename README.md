# ACL Searcher

## **Overview**
Simple interface for advanced semantic search of papers in the ACL circuit using the ColBERT retriever on paper abstracts. Up to date through January, 2025. Papers and abstracts are taken directly from the ACL master bib file, and we will try to update the index to contain the newest papers as often as we can.

---

## **Setup Instructions**

Clone the repo, and then use `pip` to install the libraries listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Usage**
1. Run the application on the host server (make sure your host exposes the 5000 port, or change it with the `--port` flag):
```bash
python app.py --web
```
2. Using a browser, connect to

```bash
http://YOUR.HOST.IP.ADDRESS:5000
```
3. Use the interface to search!

---

## **Contributing**
Feel free to open an issue or submit a pull request for improvements!

---

## **License**
[MIT License](LICENSE)