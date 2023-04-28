build:
		docker build -t fsp/pdfparse-api . 
run: build 
		docker run --env-file .env -p 10007:8080 fsp/pdfparse-api