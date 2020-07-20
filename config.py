import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    # SYSTEM Configuration +++ Better to Change IT +++

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # the seed of your token, please do change the default below
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-not-so-secret-anymore'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2:///lunch'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'

    # we send the emails only via SendGrid
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_DEFAULT_FROM = os.environ.get('SENDGRID_DEFAULT_FROM') or 'your.admin@org'

    # Google's reCaptcha keys (when enabled)
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

    # Application Specific Configuration Below

    # a reset password/confirm email token is set to expire in 5 hours (if your MX is slow)
    E_TOKEN_EXPIRES = 60 * 60 * 5

    # how to paginate about anything which needs it (labelled here as posts)
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE') or 5)

    # after how many days the lunch invite/booking expires (12h)
    LUNCH_EXPIRE_DAYS = 0.5

    # show first time users some information about their account
    LUNCH_NOOB_MODE = bool(False or os.environ.get('LUNCH_NOOB_MODE'))

    # delete users if idle/inactive for more than 90 days, or 13 weeks
    IDLEUSER_LIFETIME_WEEKS = int(os.environ.get('IDLEUSER_LIFETIME_WEEKS') or 13)

    # how long to keep an user logged in (auto-refreshes while logged in)
    SESSION_LIFETIME_MINUTES = int(os.environ.get('SESSION_LIFETIME_MINUTES') or 30)

    # wait miliseconds between auto-refreshing (incoming messages, tasks, etc)
    PAGE_REFRESH = int(os.environ.get('PAGE_REFRESH') or 10) * 1000
