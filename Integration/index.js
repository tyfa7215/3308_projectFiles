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

var username = null;

const dbConfig = {
	host: 'localhost',
	port: 5432,
	database: 'brandsense_db',
	user: 'postgres',
	password: '12345'
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

app.get('/about', function(req, res) {
	res.render('about',{
		local_css:"styles.css",
		my_title:"About Page"
	});
});
app.post('/auth', function(req, res) {
	var user = req.body.username;
	var pass = req.body.password;
	console.log(user+' , '+pass);
	if (user && pass){
		var query = "SELECT * FROM users WHERE username=$1 AND password=$2;";
		info = [user, pass]
		console.log(query, info);

		db.any(query, info).then(function (rows) {
		if (rows.length > 0){
			username = user;
			res.redirect('/')
		}
		else{
			res.send('Incorrect username or password');
		}
		res.end();

	})
		.catch(function (err) {
			console.log('ERROR, ' + err)
		    // display error message in case an error
		    request.flash('error', err);
		    res.render('index',{
		  	my_title: "Home Page",
		  	local_css:"styles.css"
			})
		})
	}
	else {
		res.send('Please enter Username and Password!');
		res.end();
	}
});
app.get('/login', function(req, res) {
	res.render('login',{
		local_css:"styles.css",
		my_title:"Login"
	});
});

//reached after choosing image to upload on main page, runs python script and displays image info
app.post('/upload', upload.single('photo'), (req, res) => {
    if(req.file) {
        //console.log(req.file.filename)
        //create child process, running python script and passing image as parameter
        var spawn = require("child_process").spawn;
        // We should do this. We can also set the 'T' to an 'F' and we would have what we had before.
        var process = spawn('python3',["./image_analysis.py","uploads/images/"+req.file.filename, 'T', username]);
		// Here is what it was
		// var process = spawn('python',["./image_analysis.py","uploads/images/"+req.file.filename] );

		//display return data from python script

		//need to parse the return data to start the SQL query stuff
		// All that need to be done is grabbing the row with the id that was spit out from the python. We do want
		// a check to make sure it didn't return "not found" or something.
		process.stdout.on('data', function(data) {
			raw_data = data.toString()
			console.log(raw_data)
			if (raw_data.includes('Error'))
			{
				// We can make this display any text. But that might not actually be valuable.
				var data = {
					'img': "uploads/images/"+req.file.filename,
					'logo': raw_data.replace('Error: ', ''),
					'url': 'N/A',
					'info': 'N/A'
				}
				res.render('display_scan',{
					local_css:"styles.css",
					my_title:"Result Page",
					result: data
				});
				return
			}
            parsed_data = raw_data.replace(/\[/g, '').replace(/\]/g, '').replace(/\'/g, "").trim()
			ids = parsed_data.split(',', 3)
			query = 'select * from logos where logo_id=$1'
			db.any(query, [ids[0]]).then(function (rows) {
				row_data = rows[0]
				var data = {
					'img': "uploads/images/"+req.file.filename,
					'logo': row_data.logo,
					'url': row_data.link,
					'info': row_data.info
				}
				res.render('display_scan',{
					local_css:"styles.css",
					my_title:"Result Page",
					result: data
				});

			})
			.catch(function (err) {
				console.log('ERROR, ' + err)
				// display error message in case an error
				request.flash('error', err);
				res.render('display_scan',{
					local_css:"styles.css",
					my_title:"Home Page"

				});
			})

			//res.send(ids[0]);
	    })
    }
    else throw 'error';
});

app.post('/uploadimg', upload.single('photo'), (req, res) => {
    if(req.file) {
		console.log('Adding image')
        //console.log(req.file.filename)
        //create child process, running python script and passing image as parameter
        var spawn = require("child_process").spawn;
		// Here is the following format for the python file.
		// image_analysis.py <relative_image_path> <T|F use db> <Username> <T|F upload iamge> <Url for logo> <description for logo> < uploading logo client(optional)>
		// So for uploading an image an example would be
		// image_analysis.py pink_nike.jpg T None T "http://www.nike.com" "Nikes Breast cancer awarness campain" Nike
		var process = spawn('python3',["./image_analysis.py","uploads/images/"+req.file.filename, 'T', 'None', 'T', req.body.url, req.body.description]);


		process.stdout.on('data', function(data)
		{
			console.log(data.toString())
			res.render('index',{
				local_css:"styles.css",
				my_title:"Home Page"
			});
		});

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
				'url': rows[i].url
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
