FROM     python
WORKDIR  /app
COPY     ./wsgi.py 	./
COPY     ./payments.py 	./
COPY     ./db.py 	./
COPY     ./test.py 	./
COPY	./requirements.txt		./
RUN     pip install --upgrade pip --no-cache-dir
RUN		pip install -r requirements.txt --no-cache-dir
CMD		["gunicorn","-w", "4","wsgi:app","--bind","0.0.0.0:5001"]

