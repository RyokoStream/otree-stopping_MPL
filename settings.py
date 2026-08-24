from os import environ

SESSION_CONFIGS = [
    dict(
        name='part1_test',
        display_name="パート1（CE測定）の単体テスト",
        num_demo_participants=1,
        app_sequence=['part1_ce'],
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'ja'
REAL_WORLD_CURRENCY_CODE = 'JPY'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '5339272332516'
