# Brandsense

The purpose of Brandsense is to allow for a more cosmetically apealing version of QR code scanning. Brandsense leverages Google Cloud Vision's machine learning to allow users to scan the actual logos of different brands that they are interested in. This gives companies the flexablitiy to use their own logo as a marketing tool rather than a QR code. Companies can sign up with us to add their logo images to our database as well as a webpage or discount code that they want the user to recieve when they scan the logo. This business model is great for company campeigns as they are able to create specialized logos for campaign purposes in order to give out promotions or advertise their website. 


INSTRUCTIONS FOR REQUIRED PACKAGES
Installation for cloud vision API.
Python: Install packages, `pip install virtualenv` and `pip install google-cloud-vision`, `pip install python-oauth2`, `pip install webcolors`,  `pip install psycopg2`(or `pip install psycopg2-binary`). And any other missing packages that give errors, use pip install and the name for the others. Note that the python file we use was written for python 3.7. Python 2 will not work.
More info on cloud vision. I didn’t follow the instructions provided but if the above doesn’t work try what they say.

Usage For Everyone: 
Use google_api_key.json file in the google doc file as the credentials for the application, look at code implementation. 
VERY IMPORTANT: Do not push this JSON file to the repository or put publically online.
For Postgres refer to the javascript file or the python for username and password.


Project tracker
https://trello.com/b/l4IH7jSw/software-dev-tracker


Directory Structure:     
|--3308_projectFiles   
&emsp;&emsp;|--css  
&emsp;&emsp;&emsp;&emsp;|--styles.css  
&emsp;&emsp;|--db   
&emsp;&emsp;&emsp;&emsp;|--db_init.sql   
&emsp;&emsp;|--img  
&emsp;&emsp;&emsp;&emsp;|--adidas_backpack.jpeg   
&emsp;&emsp;&emsp;&emsp;|--cat.jpg   
&emsp;&emsp;&emsp;&emsp;|--giraffe.jpg   
&emsp;&emsp;&emsp;&emsp;|--img1.png   
&emsp;&emsp;&emsp;&emsp;|--img2.png   
&emsp;&emsp;&emsp;&emsp;|--img3.png   
&emsp;&emsp;&emsp;&emsp;|--jaguar.jpeg   
&emsp;&emsp;&emsp;&emsp;|--jaguar_car.jpg   
&emsp;&emsp;&emsp;&emsp;|--mastercard.png   
&emsp;&emsp;&emsp;&emsp;|--mastercard_2.png   
&emsp;&emsp;&emsp;&emsp;|--nike.png   
&emsp;&emsp;|--javascript   
&emsp;&emsp;&emsp;&emsp;|--image_script.js   
&emsp;&emsp;|--node_modules   
&emsp;&emsp;|--views   
&emsp;&emsp;&emsp;&emsp;|--about.pug   
&emsp;&emsp;&emsp;&emsp;|--display_scan.pug   
&emsp;&emsp;&emsp;&emsp;|--index.pug   
&emsp;&emsp;&emsp;&emsp;|--login.pug   
&emsp;&emsp;&emsp;&emsp;|--scans.pug   
&emsp;&emsp;|--.DS_Store   
&emsp;&emsp;|--.gitignore   
&emsp;&emsp;|--README.md   
&emsp;&emsp;|--image_analysis.py   
&emsp;&emsp;|--index.js   
&emsp;&emsp;|--package-lock.json   
&emsp;&emsp;|--package.json   
