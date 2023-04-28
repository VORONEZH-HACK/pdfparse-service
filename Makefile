build:
		docker build -t fsp/pdfparse-api . 
run: build 
		docker run --env-file .env -p 10005:8080 fsp/pdfparse-api