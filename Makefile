build:
		docker build -t fsp/pdfparse-api . 
run: build 
		docker run --env-file .env -p 10002:8080 fsp/pdfparse-api