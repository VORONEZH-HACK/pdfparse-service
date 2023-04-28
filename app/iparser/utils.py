import io
import os
import re
from collections import defaultdict
from datetime import datetime
import requests

import docx2txt
import nltk
import pandas as pd
import textract
from dateutil import relativedelta
from docx import Document
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pdfminer.high_level import extract_text
from PyPDF2 import PdfFileReader

from . import cs as cs


def read_text_from_pdf(pdf_file_path):
    if isinstance(pdf_file_path, io.BytesIO):
        text = extract_text(pdf_file_path)
    else:
        with open(pdf_file_path, 'rb') as file:
            text = extract_text(file)
    return text.split('\n')


def count_pages_in_pdf(file_name):
    if isinstance(file_name, io.BytesIO):
        pdf = PdfFileReader(file_name)
        total_pages = pdf.getNumPages()
    else:
        with open(file_name, 'rb') as file:
            pdf = PdfFileReader(file)
            total_pages = pdf.getNumPages()
    return total_pages


def read_text_from_docx(document_path):
    doc = Document(document_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return ' '.join(full_text)


def read_text_from_doc(doc_file_path):
    try:
        file_text = textract.process(doc_file_path).decode('utf-8')
    except KeyError:
        file_text = ' '
    return file_text


def gather_text(file_path, file_extension):
    text = ''
    if file_extension == '.pdf':
        text = read_text_from_pdf(file_path)
    elif file_extension == '.docx':
        text = read_text_from_docx(file_path)
    elif file_extension == '.doc':
        text = read_text_from_doc(file_path)
    return text


def get_sections_for_grads(raw_text):
    lines = [line.strip() for line in raw_text.split('\n')]
    entity_dict = defaultdict(list)
    curr_key = None
    for line in lines:
        if len(line) == 1:
            p_key = line
        else:
            p_key = set(line.lower().split()) & set(cs.GRAD_RESUME_SECTIONS)
            p_key = list(p_key)[0] if p_key else None

        if p_key in cs.GRAD_RESUME_SECTIONS:
            curr_key = p_key
        elif curr_key and line:
            entity_dict[curr_key].append(line)

    return dict(entity_dict)


def extract_entities_with_custom_model(doc_obj):
    entities = defaultdict(list)
    for entity in doc_obj.ents:
        entities[entity.label_].append(entity.text)
    for key in entities.keys():
        entities[key] = list(set(entities[key]))
    return dict(entities)


def calculate_total_experience(exp_list):
    exp_tuples = []
    for line in exp_list:
        match = re.search(
            r'(?P<start>\w+.\d+)\s*(\D|to)\s*(?P<end>\w+.\d+|present)',
            line,
            re.I
        )
        if match:
            exp_tuples.append(match.groups())
    total_exp = sum(
        [calculate_months_between_dates(i[0], i[2]) for i in exp_tuples]
    )
    return total_exp


def calculate_months_between_dates(start_date, end_date):
    if end_date.lower() == 'present':
        end_date = datetime.now().strftime('%b %Y')

    try:
        if len(start_date.split()[0]) > 3:
            start_date = ' '.join(start_date.split()[:2])
            start_date = start_date[:3] + start_date.split()[1]
        if len(end_date.split()[0]) > 3:
            end_date = ' '.join(end_date.split()[:2])
            end_date = end_date[:3] + end_date.split()[1]
    except IndexError:
        return 0

    try:
        start_date = datetime.strptime(str(start_date), '%b %Y')
        end_date = datetime.strptime(str(end_date), '%b %Y')
        experience_in_months = relativedelta.relativedelta(
            end_date, start_date)
        experience_in_months = experience_in_months.years * \
            12 + experience_in_months.months
    except ValueError:
        return 0

    return experience_in_months


def get_professional_sections(raw_text):
    lines = [line.strip() for line in raw_text.split('\n')]
    entity_dict = defaultdict(list)
    curr_key = None
    for line in lines:
        if len(line) == 1:
            p_key = line
        else:
            p_key = set(line.lower().split()) & set(
                cs.PROFESSIONAL_RESUME_SECTIONS)
            p_key = list(p_key)[0] if p_key else None

        if p_key in cs.PROFESSIONAL_RESUME_SECTIONS:
            curr_key = p_key
        elif curr_key and line:
            entity_dict[curr_key].append(line)

    return dict(entity_dict)


def retrieve_email(resume_text):
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", resume_text)
    return email[0].split()[0].strip(';') if email else None


def find_name(nlp_doc, pattern_matcher):
    pattern_matcher.add('NAME', None, cs.NAME_PATTERN)

    matches = pattern_matcher(nlp_doc)

    for match_id, start, end in matches:
        span = nlp_doc[start:end]
        if 'name' not in span.text.lower():
            return span.text


def find_mobile_number(resume_text, custom_regex=None):
    if not custom_regex:
        mob_num_pattern = r'''(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{7})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'''
        phone_numbers = re.findall(re.compile(mob_num_pattern), resume_text)
    else:
        phone_numbers = re.findall(re.compile(custom_regex), resume_text)
    return ''.join(phone_numbers[0]) if phone_numbers else None


def identify_skills(nlp_doc, noun_phrases, skills_filepath=None):
    tokens = [token.text for token in nlp_doc if not token.is_stop]
    skills = pd.read_csv(skills_filepath or os.path.join(
        os.path.dirname(file), 'skills.csv')).columns
    skills_identified = [token for token in tokens if token.lower() in skills]

    for noun_phrase in noun_phrases:
        noun_phrase = noun_phrase.text.lower().strip()
        if noun_phrase in skills:
            skills_identified.append(noun_phrase)

    return list(set([skill.capitalize() for skill in skills_identified]))


def clean_text(text, to_lower=True):
    return text.lower().strip() if to_lower else text.strip()


def extract_degree_and_year(nlp_doc):
    degree_and_year = {}
    try:
        for i, text in enumerate(nlp_doc):
            for word in text.split():
                rd = re.sub(r'[?|$|.|!|,]', r'', word)
                if word.upper() in cs.EDUCATION and word not in cs.STOPWORDS:
                    degree_and_year[word] = text + nlp_doc[i + 1]
    except IndexError:
        pass

    education = []
    for degree, text in degree_and_year.items():
        year = re.search(re.compile(cs.YEAR), text)
        education.append((degree, ''.join(year.group(0))) if year else degree)

    return education


def extract_experience_details(resume_text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    word_tokens = nltk.word_tokenize(resume_text)

    filtered_tokens = [lemmatizer.lemmatize(
        w) for w in word_tokens if w not in stop_words]
    pos_tags = nltk.pos_tag(filtered_tokens)
    cp = nltk.RegexpParser('P: {<NNP>+}')
    chunk_tree = cp.parse(pos_tags)

    experience_phrases = [" ".join([word for word, tag in subtree.leaves()])
                          for subtree in chunk_tree.subtrees(filter=lambda t: t.label() == 'P') if len(subtree.leaves()) >= 2
                          ]

    experience_details = [
        phrase[phrase.lower().index('experience') + 10:]
        for phrase in experience_phrases
        if 'experience' in phrase.lower()
    ]


def translate(texts):
    folder_id = '<идентификатор каталога>'
    target_language = 'ru'

    body = {
        "targetLanguageCode": target_language,
        "texts": texts,
        "folderId": 'b1g5oiosrr37uepspdk0',
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(cs.TOKEN)
    }

    response = requests.post(
        'https://translate.api.cloud.yandex.net/translate/v2/translate',
        json = body,
        headers = headers,
        timeout=None,
    )

    return response.text
