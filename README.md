# Lunch Roulette (OSS)

### by its original AUTHORS

Ciprian bought and we took heavy inspiration from the [Flask Mega Tutorial](https://courses.miguelgrinberg.com/p/flask-mega-tutorial) which we wholeheartedly recommend you to read in order to quickly grasp how we built our (now open sourced under a [BSD-3 license](LICENSE)) implementation of the [decade old Lunch Roulette idea](https://hbr.org/2013/01/a-new-way-to-network-inside-yo).

[WE](AUTHORS) have enjoyed running [our Lunch Roulette code](https://www.lunch-roulette.org/) on [Heroku](https://www.heroku.com/) which was, and still is, a great fit for this implementation. The Flask Mega Tutorial (mentioned above) has a public page about [how to deploy your Flask app (or Lunch Roulette clone) in Heroku](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xviii-deployment-on-heroku).

P.S. at this moment we have no further plans to update this codebase.

### Features

- [x] built with [Flask](https://palletsprojects.com/p/flask/): safe logins, easy DB migrations
- [x] security, auto-scaling, data safety based on [Heroku](https://www.heroku.com/)
- [x] simple (and GDPR consciuos) user sign-up page
- [x] (GDPR bonus) purge of inactive accounts (90 days)
- [x] password reset support (with expiring web link)
- [x] support for Gravatar(s) (no pictures stored)
- [x] simple and super simple user profile page
- [x] very simplistic internal messaging system
- [x] users' session auto-timeout support
- [x] all user content visible only after users' authentication
- [x] company detection based on their own TLDs (@domain)
- [x] multi-user and multi-company support in same instance
- [x] company admin(s) and super admin(s) (more visibility)
- [x] invites and random lunches only inside same company
- [x] browser/user time zone detection (when is lunch time?)
- [x] SendGrid support for sending (all) emails
- [x] reCaptcha support (disabled by default)
- [x] Google Analytics support
- [x] Satismeter support
- [x] Freshchat support

#### Installing your developer environment

- run ./runme.sh to get the NTLM proxy, PostgreSQL and required deps up and running
- then later, run ./local/install.sh to get a local python virtualenv for faster iteration

#### NOTE: use _git grep your_ to find the ids & keys you should change before deploying it
