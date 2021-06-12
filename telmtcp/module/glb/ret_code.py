# ***********************************************************************************
# File Name: ret_code.py
# Author: Dimitar
# Created: 2020-04-16
# Description: Return Codes Constants For Modules Of MTBDashboard
# -----------------------------------------------------------------------------------

# --------------- Constants For User Authentication --------------- #
AUTH_UNKOWN_ERROR                = -101
AUTH_SUCCESS                     = 0
AUTH_ACCOUNT_NOT_FOUND           = 101
AUTH_PHONE_NUMBER_DUPLICATED     = 102
AUTH_WRONG_PWD                   = 103
AUTH_ACCOUNT_DISABLED            = 104

AUTH_ALERT_STRING = {
    AUTH_UNKOWN_ERROR: 'Sorry, something went wrong',
    AUTH_ACCOUNT_NOT_FOUND: 'Account is not recognized',
    AUTH_PHONE_NUMBER_DUPLICATED: 'Phone number is duplicated. Please use your email instead.',
    AUTH_WRONG_PWD: 'Account is not recognized',
    AUTH_ACCOUNT_DISABLED: 'Account is disabled'
}

# --------------- Constants For User Registration --------------- #
REG_UNKOWN_ERROR                = -101
REG_SUCCESS                     = 0
REG_EXISTING_EMAIL              = 101
REG_EXISTING_PHONE_NUMBER       = 102
REG_INCORRECT_PHONE_NUMBER      = 103
REG_TOO_MANY_REQUESTS           = 104
REG_RISK                        = 105

