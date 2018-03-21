# UdacityServerProject
This is a Linux Server that use Amazon Lightsail to host a preview developed project (https://github.com/ghsmaniotto/Udacity/tree/master/Project-4)

This project is not working today because the Amazon trial license was expired. But I did this project as requirement to graduate in Full-Stack Udacity course. 
# Project info's

## The user
  The `server-admin` is the user that you can access the server by the Private/Public Key.

## The IP address and SSH port
  The IP address is `52.14.137.130`
  The SSH port is `2200`
  To access the server you need type:
  ```bash
  ssh server-admin@52.14.137.130 -p 2200 -i path/to/the/key
  ```
## The application url
  The complete url of the project is `http://52.14.137.130`
  
# Installed softwares
Some of the softwares that was installed was:
- Pip (`sudo apt-get install python-pip`)
- Flask (`sudo pip install Flask`)
- Postgres (`sudo apt-get install postgresql`)
- Apache2 (`sudo apt-get install apache2`)
- Libapache2-mod-wsgi (`sudo apt-get install libapache2-mod-wsgi`)
- SQLAlchemy (`pip install sqlalchemy `)
- PassLib (`pip install passlib`)
- Flask_httpauth (`pip install flask_httpauth`)
- HttpLib2 (`pip install httplib2`)
- Requests (`pip install requests`)
- OAuth2Client (`pip install oauth2client`)

# Configurations Changes
 Fews configurations were changed from the original project (https://github.com/ghsmaniotto/Udacity/tree/master/Project-4).

### Clone the projecto to /var/www/html
A repository named `UdacityLinuxServer` was cloned to the `var/www/html`. Because that, the directory name that contains all the application is:
`/var/www/html/UdacityLinuxServer`

This path will be defined in some files. The next step shows how.

### Install the mod-wsgi 
The `mod-wsgi` is an application handler to Apache. The `/etc/apache2/sites-enabled/000-default.conf` was modified according our especification. This file tells Apache how to respond to requests. 
We add this lines in thr file, between the `<VirtualHost *:80>` and `</VirtualHost>`:
```javascript
  WSGIDaemonProcess application home=/var/www/html/UdacityLinuxServer user=smaniotto group=smaniotto threads=1
  WSGIScriptAlias / /var/www/html/UdacityLinuxServer/application.wsgi
  
  <Directory /var/www/html/UdacityLinuxServer>
          WSGIProcessGroup application
          WSGIApplicationGroup %{GLOBAL}
          Order deny,allow
          Allow from all
  </Directory>
```

### Add `application.wsgi` file
This `application.wsgi` need to be added to handle the requests. In my case, this file contains:
```python
import sys
sys.path.insert(0, '/var/www/html/UdacityLinuxServer')

from app import catalog_app as application
```
In general, this file need to import the Flask application, in my case, the application is named `catalog_app`.

### Sudo user and keys authentication
We add the `server-admin` as sudo user and configure the SSH to only accept the key authentication.
Besides, we change the firewall configuration to accept SSH, NTP and HTTP.



 

