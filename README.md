# Igni et Ferro - a Multi-Container Django Web Application 

A demonstrational Django-Nginx-Docker back-end website designed as a website for a Minecraft server.

### TL;DR

- Social-media-style website for a closed videogame community
- Django back-end, multi-container setup (Docker)
- Nginx, Redis, Celery, PostgreSQL
- Email-based approval system and custom security measures
- Login-protected media files serving
- Profile pages with auto-generated profile pictures
- Posts, likes, comments, website achievements
- Optional SSL setup
### Sections:

- [About this project](#about-this-project)
- [Features](#features)
- [Running the project](#running-the-project)
- [Credits](#credits)

## About this project

This website was built to demonstrate and enhance my development skills in building websites. It was designed as a website, functioning as a social media platform, for a private community of a small Minecraft server. Everyone here can share their stories and media related to the server and interact with each other by commenting and liking each other's posts and profiles.

It showcases how different back-end technologies can be used to build a more complex project. This project used **Django** web framework to build the website; **Nginx** server and reverse proxy to serve files and direct users to the website; **Celery** for queueing tasks and **Celery Beat** for staging periodic ones; **Redis** as a broker for Celery and as a cache back-end at the same time; **PostgreSQL** as the database system. All of these components can be launched in **Docker** containers to boot up the website and run it instantly, or can be easily switched to other non-containerized services (e.g. AWS services like RDS, ElastiCache, etc.) via .env file's variables.

Working on the project gave me a deeper understanding of website designing process, including the peculiarities and necessity of data caching, importance and ways to implement security measures, and the overall structure of multi-container applications and their basic deployment.

### How should the website be used?

#### Signing up

The website is closed from the public view and can be accessed by registered and approved users only. Registration process is implemented via an application review system: a person should fill in the registration form which includes the application so that the website admins can review it and either approve or decline it through Django admin. The person will receive an email notification based on the outcome of this process. 

>ℹ️ Note: **The website validates whether the username chosen for the account actually exists, so it should be an existing Minecraft account's username** (for testing purposes, during the registration you may use such usernames as Steve, Alex, Jason, Henry).

The password reset system is also implemented.

A system that limits login, registration, password reset attempts is implemented to prevent any brute-force attacks or abuse of the website's resources.

#### Website functionality

You can make posts in a set of admin-defined categories. The website uses [CKEditor5](https://ckeditor.com/) rich text editor which supports embedding different types of media into the posts you create, formatting the text, creating tables and so on.

You can comment and like posts made by users of the website, and you will receive notifications when other interact with your posts.

Every active user has a profile where they can specify their bio, a signature (that is automatically added at the end of every their post), add pictures to their page (that can be hidden later). Also, their like and blog count, a list of their posts, website achievements and profile comments are shown there.

The profile picture (PFP) is generated automatically based on the username the user specifies for the account, and is based on their Minecraft skin. It gets refreshed once in a set period of time, or can be refreshed manually (there is a refresh rate limit to prevent triggering API abuse limits).

A system of website achievements tracks notable actions made by the users and rewards them with achievements (like creating X posts, getting X likes, making X comments, etc.)

You can follow other users to keep track of their new posts and receive updates about their activity in your Timeline, which shows both the posts and media uploaded by the users you follow in the chronological order.

## Features

This project showcases the usage of:
- Redis
	- [users/helpers/mcuser.py](users/helpers/mcuser.py)
	- [users/helpers/profiles.py](users/helpers/profiles.py#L10-L21) (**rate limits**)
	- [users/helpers/authentication.py](users/helpers/authentication.py#L76-L123) (**attempt restrictions class**)
	- [ief/settings.py](ief/settings.py#L229-L240)
	- [ief/urls.py](ief/urls.py#L29) (**caching whole page**)
	- [users/views.py](users/views.py#L419-L452) (**login brute-force attack protection**)
- Celery
	- [users/tasks.py](main/users/tasks.py) (**email sending**)
- Celery Beat
	- [dumps/celery_beat_data.json](dumps/celery_beat_data.json) (**PFP update**)
- Third Party APIs
	- [users/helpers/mcuser.py](users/helpers/mcuser.py#L10-L50)
- Image Processing
	- [users/helpers/mcuser.py](users/helpers/mcuser.py#L53-L82) (**PFP creation**)
- Logging
	- [users/views.py](users/views.py)
	- [users/helpers/authentication.py](users/helpers/authentication.py#L56)
	- [ief/settings.py](ief/settings.py#L169-L226)

And has other functionality worth mentioning:
- Both function-based and class-based view usage
- [Custom Validators (for passwords)](users/helpers/password_validation.py)
- [Signals](users/signals.py)
- [Caching](users/helpers/mcuser.py)
- [Fixtures](dumps/)
- [Email Sending](common/email.py)
- [Password Reset](users/views.py#L476-L519)
- [Custom HTTP Error Pages](ief/urls.py#L38-L41)
- [Django Messages](users/views.py)

- Security measures
	- [URL Enumeration Protection](blogs/views.py#L182-L217)
	- [Login Brute-force Attack Protection](users/views.py#L419-L452)

## Running the project

You should first clone the project on your local machine to proceed with further configuration. You can do that this way:
```shell
git clone https://github.com/mykdolnyk/ief-django-website.git
cd ief-django-website
```
#### Configuring the .env file

While the website project is preconfigured for the most related services (PostgreSQL DB, Celery, Redis), you still should connect your own email service to the website for it to fully show its potential and function flawlessly. 

If you omit this step, the password reset functionality, as well as registration application approval/decline notifications will not work (it shouldn't cause any other issues though).

By default, the project will use the `test.env` .env file that is provided in its root folder. This file stores details that should not be hardcoded or are sensitive and shouldn't be left in the code, including the details related to an email service. 

Open the `test.env` file and locate these fields:
```properties
...
# These properties should be configured manually:
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
...
```

Fill in these properties with the required information corresponding to your email service provider. You may also tweak other properties in your file, if you need to.

#### Docker Compose

Once the project is successfully cloned, first ensure that you have Docker Desktop installed and running. Then you would need to build the containers and configure the project. Enter the following commands one by one when first starting the app:
1. Build the image:
```shell
docker compose build
```
2. Start the project itself
```shell
docker compose up
```
*When launching the app again, entering only the `docker compose up` command is sufficient and recommended.*

The website should already be set up, loading all the required dependencies and fixtures automatically, and you should be able to access it by visiting this URL:
```
http://localhost/
```

#### Approving user applications

> Application approval functionality is disabled by default to make the testing process much easier. You can register an account and try logging into it instantly. If you wish to test out the application system, set the environment variable DJANGO_AUTO_APPROVAL to False.
> Note: you will have to create a superuser first if you decide to do that. Superuser will not have a displayable profile on the website and should log into the admin panel only. Generally, you would create such users to approve or decline applications sent by other people.

To approve/decline applications sent by new users, you would need to log into Django Admin interface, and go to the "**Applications**" tab in the "**Users**" section. Click on the application entry and change its status ("**Application status**") to "**Approved**", save the changes. It will send an email to the user and allow them to log into their account.

#### Shutting down the project

Once you are done with testing, you can turn off the website and remove the containers with this command:
```shell
docker compose down
```
## Credits

This project uses [CKEditor 5](https://ckeditor.com), licensed under the [GPL 2+](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html). 
CKEditor 5 is an open-source rich text editor provided by CKSource. More details can be found at [ckeditor.com](https://ckeditor.com).

The frames for website's achievements were made by [Carol_dron](https://github.com/Keymagen).
