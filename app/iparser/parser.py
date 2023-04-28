import io
import multiprocessing as mp
import os

import spacy
from spacy.matcher import Matcher

from . import utils as ut


class ParserForResume:

    def __init__(self, resume, skills_file=None, custom_regex=None):
        self.skills_file = skills_file
        self.custom_regex = custom_regex
        self.matcher = Matcher(spacy.load('en_core_web_sm').vocab)
        self.details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
        }
        self.resume = resume
        resume_ext = self.__get_extension()
        raw_text = ut.translate(ut.gather_text(self.resume, resume_ext))
        self.text = ' '.join(raw_text.split())
        self.nlp = spacy.load('en_core_web_sm')(self.text)
        self.custom_nlp = spacy.load(os.path.dirname(
            os.path.abspath(__file__)))(raw_text)
        self.noun_chunks = list(self.nlp.noun_chunks)
        self.__parse_resume()

    def __get_extension(self):
        if not isinstance(self.resume, io.BytesIO):
            return os.path.splitext(self.resume)[1]
        else:
            return '.' + self.resume.name.split('.')[1]

    def get_data(self):
        return self.details

    def __parse_resume(self):
        cust_ent = ut.extract_entities_with_custom_model(self.custom_nlp)
        name = ut.find_name(self.nlp, pattern_matcher=self.matcher)
        email = ut.retrieve_email(self.text)
        mobile = ut.find_mobile_number(self.text, self.custom_regex)
        skills = ut.identify_skills(
            self.nlp, self.noun_chunks, self.skills_file)
        entities = ut.get_sections_for_grads(self.text)
        self.details.update({
            'name': self.__get_entity(cust_ent, 'Name', default=name),
            'email': email,
            'mobile_number': mobile,
            'skills': skills,
            'college_name': self.__get_entity(entities, 'College Name'),
            'degree': self.__get_entity(cust_ent, 'Degree'),
            'designation': self.__get_entity(cust_ent, 'Designation'),
            'company_names': self.__get_entity(cust_ent, 'Companies worked at'),
            'experience': self.__get_experience(entities),
            'total_experience': self.__get_total_experience(entities),
            'no_of_pages': ut.count_pages_in_pdf(self.resume),
        })

    def __get_entity(self, entities, entity, default=None):
        return entities.get(entity, [default])[0]

    def __get_experience(self, entities):
        return entities.get('experience')

    def __get_total_experience(self, entities):
        try:
            return round(ut.calculate_total_experience(entities['experience']) / 12, 2)
        except KeyError:
            return 0


def result_wrapper(resume):
    return ParserForResume(resume).get_data()


if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    resumes = [os.path.join(root, filename) for root, _, filenames in os.walk(
        'resumes/') for filename in filenames]
    results = [pool.apply_async(result_wrapper, args=(
        resume,)).get() for resume in resumes]
