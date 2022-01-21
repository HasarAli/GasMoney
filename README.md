# GasMoney
A platform to connect passengers with drivers on long rides to save money, time, and the planet.

GasMoney is hosted on Google App Engine [here](https://sonic-passkey-336007.ue.r.appspot.com/)

## Tools
Flask, a python micro framework, is used to build the backend of the website. Jinja2, JavaScript, HTML, and Bootstrap have been utilized in making the frontend.
Database communication is handled by Flask-SqlAlchemy. The database used in production environment is a MySql instance hosted on Google Cloud, however, it was developed with a local Sqlite databse.
Gasmoney's email client is SendGrid, and its SMS client is Twilio. They are used for reseting passwords and verifying credentials.
