const express = require('express')
const bodyParser = require('body-parser')
const app = express()
const port = 3000
const pug = require('pug')
const multer = require('multer')//package for uploading images
const upload = multer({dest: __dirname + '/uploads/images'});//directory to store uploaded images
const pgp = require('pg-promise')();


app.use(bodyParser.json())
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
)

const username = "ian";

const dbConfig = {
	host: 'localhost',
	port: 5432,
	database: 'brandsense_db',
	user: 'postgres',
	password: '123'
};

let db = pgp(dbConfig);

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
        // We should do this. We can also set the 'T' to an 'F' and we would have what we had before.
        var process = spawn('python',["./image_analysis.py","uploads/images/"+req.file.filename, 'T', username]);
		// Here is what it was
		// var process = spawn('python',["./image_analysis.py","uploads/images/"+req.file.filename] );

		//display return data from python script

		//need to parse the return data to start the SQL query stuff
		// All that need to be done is grabbing the row with the id that was spit out from the python. We do want
		// a check to make sure it didn't return "not found" or something.
		process.stdout.on('data', function(data) {
		    raw_data = data.toString()
            parsed_data = raw_data.replace(/\[/g, '').replace(/\]/g, '').replace(/\'/g, "").trim()
            ids = parsed_data.split(',', 3)

		    if (ids.length > 0)
		    {
		        // DB stuff to get relevant row
		        res.send(ids);
		    }
		    else
		    {
		        res.send(raw_data);
		    }
	    } ) 
    }
    else throw 'error';
});

app.get('/scans',function(req,res){
	// This is the only safe way to have parameters for postgres
    query = "select * from userHistory where username=$1 ORDER BY ts DESC LIMIT 10"
	// callback

    db.any(query, [username]).then(function (rows) {
		scan_hist = []
		for (i = 0; i < rows.length; i++)
		{
			// This displays an image, from the database
			// I removed the colors and text option as they aren't useful to display.
			// TODO change db so we store relevant row and then we can grab the info in node
			var history = {
				'img': 'data:image/jpg;base64,' + Buffer.from(rows[i].img).toString('base64'),
				'logo': rows[i].logo,
				'url': "N/A"
			}
			scan_hist.push(history)
		}
	    res.render('scans',{
	        my_title: "Scans",
	        local_css:"styles.css",
	        user_history: scan_hist,
	    })

	})
	.catch(function (err) {
		console.log('ERROR, ' + err)
	    // display error message in case an error
	    request.flash('error', err);
	    res.render('scans',{
	  my_title: "Scans",
	  local_css:"styles.css",
	  data: '',
	})
	})
});

app.listen(port, () => {
  console.log(`App running on port ${port}.`)
})