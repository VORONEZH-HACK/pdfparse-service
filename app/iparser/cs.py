from nltk.corpus import stopwords

NAME_PATTERN = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

EDUCATION = [
    'BE', 'B.E.', 'B.E', 'BS', 'B.S', 'ME', 'M.E',
    'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH',
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
]

NOT_ALPHA_NUMERIC = r'[^a-zA-Z\d]'

NUMBER = r'\d+'

MONTHS_SHORT = r'''(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)
                   |(aug)|(sep)|(oct)|(nov)|(dec)'''
MONTHS_LONG = r'''(january)|(february)|(march)|(april)|(may)|(june)|(july)|
                   (august)|(september)|(october)|(november)|(december)'''
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
YEAR = r'(((20|19)(\d{2})))'

STOPWORDS = set(stopwords.words('english'))

PROFESSIONAL_RESUME_SECTIONS = [
    'experience',
    'education',
    'interests',
    'professional experience',
    'publications',
    'skills',
    'certifications',
    'objective',
    'career objective',
    'summary',
    'leadership'
]

GRAD_RESUME_SECTIONS = [
    'accomplishments',
    'experience',
    'education',
    'interests',
    'projects',
    'professional experience',
    'publications',
    'skills',
    'certifications',
    'objective',
    'career objective',
    'summary',
    'leadership'
]

TOKEN = 't1.9euelZqYz5qTy5Kax8ebip3Lms3Ox-3rnpWanc7GkYyXnJ6SzJuRmZzKnJHl8_dNf1Fd-e9rGgcN_t3z9w0uT13572saBw3-.voVa2e9CMnGo8s1mk8Kjz1qVwvlVcVVRwQDn2xwRVfq9vOykOsHiQrgyvPw-y7J4lC4hyvfc7E4kRnHj0AH5CQ'
