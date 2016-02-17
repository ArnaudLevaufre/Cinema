# Cinema

Cinema is a web application which provide a fancy movie library. Wether you run
it on your local network or on a public server it gives you access to your
movie database from any device by direct download or streaming.

![](https://img.bananium.fr/arnaud/cinema_home.png)

![](https://img.bananium.fr/arnaud/cinema_watch.png)

![](https://img.bananium.fr/arnaud/cinema_watchlist.png)


## Features

### Current features

- Automatic informations and poster fetching
- Automatic movie recognition from filename
- Direct download
- Movie managment and edition
- Movie streaming for .mp4 movies (HTML5 player)
- Notifications of newly available movies
- Random movie
- Search

### Planned features
- watchlist
- favorite movies
- additional movie information (actors, producer ...)
- ...

## Installation
### Requirements

You will need python 3.x and pip.

First clone the project then procede to install the dependencies like so

```
pip install -r requirements.txt
```
### Configuration

#### Application

Edit the file `cinema/settings.py`. The configuration you should change are the following ones

##### LOGIN_REQUIRED
Setting this to True will ensure only logged user can access the different pages. Setting this to False allows anyone a public access to the movies.

##### DATABASES
You may want to change the database settings to use mysql or postgresql instead of sqlite. Refer to the django documentation for more informations.


#### Nginx

If you plan to run this application on a production environment I recommand to
use nginx and uwsgi. A uwsgi configuration file is provided. Edit it to suit
your needs and then run the uwsgi server like so:

```
uwsgi uwsgi.ini
```

Then configure nginx so serve the static files and forward incoming travic to uwsgi. The following configuration can be used as a starting point.

```
server {
    listen *:80;
    # server_name cinema.example.com;

    root /path/to/project/directory/cinema;
    error_log /var/log/nginx/cinema.log crit;

	location /media {
		autoindex off;
		alias /path/to/project/directory/cinema/media;
	}

	location /static {
		autoindex off;
		alias /path/to/project/directory/cinema/collected_static;
	}

    location / {
		include uwsgi_params;
		uwsgi_pass 127.0.0.1:1234;
    }
}

```
You will then need to collect static files so run the following command:

```
./manage.py collectstatic
```


### Running the app

Once you are satisfied with your settings you have to install the database migrations like so:

```
./manage.py migrate
```

You should start by adding a movie directory by executing the following command line
```
./manage.py add /path/to/movie/directory
```
Or by visiting the django administration site.

Then update the movie database simply run.

```
./manage.py update
```

If you often add new movies you should install a cron job which run this command on a regular basis.

Then you can run the django server
```
./manage.py runserver 127.0.0.1:1234
```

Visit http://127.0.0.1:1234 and you should have access to your movie database.
