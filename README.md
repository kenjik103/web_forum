# ClassQuery
#### Video Demo:  https://youtu.be/LZRGhLAoh44
#### Site URL: https://kenjik103.pythonanywhere.com
#### Description:
Built as a final project for Harvardx's CS50 Program. Uses **Flask** framework with basic **HTML, CSS**, as well as a **Sqlite3** database. 

Because this was my first expirience with web-dev, I wanted to create something relatively simple. I figured a forum was perfect for this, as it was really just text that I had to deal with. I'm a student too, so thats why I ended up tayloring it for classroom use specifically.

#### File Structure

Files are pretty standard; the /templates directory keeps all the html, app.py contains all the flask routing, and helpers.py contains all my helper functions. Only thing worth noting is the .scss file. I used a few Bootsrap templates, so Sass was used to customize everything on the css end. All my work was done in main.scss; both main.css.map and main.css are computer-generated translations of the work I did in main.scss.

#### Login + Register

Login/Register system is pretty standard. Register takes in a username, and makes the user enter their desired password twice. It checks to make sure they're valid, and hashes the password using whatever hash werkzeug security uses. It then stores all of that inside a sqlite3 db (inside the "user' table) along side a unique id and user type (student or teacher).

Login just takes the inputted username + password and looks for it in the db.

If any invalid inputs are entered the page simply refreshes

#### Create Class

If the user type is a teacher account, they have the ability to create classes. Creating a class involves teachers entering their desired class title, a description, and picking one of four background images. A unique class code is generated using a custom function I wrote inside helpers.py. All of that information is then inserted inside the database (inside the "discussion" table). 

#### The Class

The created class serves as a platform for class discussion. 
Posts can be made, and contain a post title and body. These, along side a timestamp, user_id, and class_code, go into the database(inside the "discussion" table). This gives me enough information to display and sort the post title, body, username, and timestamp. Posts are sorted so the newest posts appear at the top of the page

Replys work in a similar fassion. The reply body, corresponding main post id, user id, class code, and timestamp all go into the database (under the "replys" table) and are subsequently displayed and sorted. New replys are displayed at the bottom. The site knows which replys go under which posts by using a hashmap. Every time a reply is sent, it loads it into this hashmap with the corresponding post id as its key. That way, for every main post it can check if it has any replys stored underneath it as values.

#### Join Class

Students don't get to create classes. Instead, the get the "Join Class" feature. It simply prompts them for a code (that presumably their teacher would provide) and allows them to enter the class if the code is correct.