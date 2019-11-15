const express = require('express')
const bodyParser = require('body-parser')
const app = express()
const port = 3000
const pug = require('pug')
const multer = require('multer')//package for uploading images
const upload = multer({dest: __dirname + '/uploads/images'});//directory to store uploaded images

app.use(bodyParser.json())
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
)

app.set('view engine', 'pug');
app.use(express.static(__dirname + '/'));

//root page, displays index.pug using styles.css
app.get('/', function(req, res) {
	res.render('index',{
		local_css:"styles.css", 
		my_title:"Home Page"
	});
});

//reached after choosing image to upload on main page, runs python script and displays image info
app.post('/upload', upload.single('photo'), (req, res) => {
    if(req.file) {
        //console.log(req.file.filename)
        
        //create child process, running python script and passing image as parameter
        var spawn = require("child_process").spawn;
		var process = spawn('python',["./image_analysis.py","uploads/images/"+req.file.filename] );

		//display return data from python script


		//need to parse the return data to start the SQL query stuff
		process.stdout.on('data', function(data) { 
	        res.send(data.toString()); 
	    } ) 
    }
    else throw 'error';
});

app.listen(port, () => {
  console.log(`App running on port ${port}.`)
})