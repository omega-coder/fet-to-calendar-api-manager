# FET Timetable to Google Calendar

Export FET generated timetable (School schedule timetable) to Google Calendar using google calendar API

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project was developped using **Python 3**, so you obviously need **python 3** installed on your machine.You can download python [here](https://www.python.org/), make sure you download python 3 and preferably the last version.

You can install the other requirements using pip from the requirement.txt file


```bash
pip install -r requirements.txt
```

### Deployment

## 1. Get a CLIENT_ID and CLIENT_SECRET using the google calendar api console.
## 2. set up environment variables for the app.
    
```bash
    export GOOGLE_OAUTH_CLIENT_ID="xxxxxxxxxx-xxxxxxxxxxxxxxxxx.apps.googleusercontent.com"
    export GOOGLE_OAUTH_CLIENT_SECRET="xxxxxxxxxxxxxxxx-xxxxxx"
```
## 3. Run the app.

```bash
    python app.py
```

Or use gunicorn server (**Recommended**)

```bash
    gunicorn --bind 0.0.0.0:5000 app:app 
``` 

## Built With

* [Python3](https://www.python.org/) - The main used language.
* [Flask](https://palletsprojects.com/p/flask/) - The web framework used.
* [Bootstrap 4 and MDB](https://getbootstrap.com/) - For the UI
* [Javascript](https://www.javascript.com/) - Interaction between UI and Back-end
* [Calendar API](https://developers.google.com/calendar/) - for events and calendars management.


## Authors

* **CHERIEF Yassine** - *Initial work* - [omega-coder](https://omega-coder.me)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* NOT YET.
