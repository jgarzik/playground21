
import json

class WorkTemplate(object):
    def __init__(self, str_in=None):
        self.obj = None
        if not str_in is None:
            self.obj = json.loads(str_in)

    def set(self, obj_in):
        self.obj = obj_in

    def set_answers(self, obj_in):
        self.answers = obj_in

    def load(self, str_in):
        self.obj = json.loads(str_in)

    def valid_questionlist(self):
        if (not 'questions' in self.obj or
            not isinstance(self.obj['questions'], list)):
            return False

        for q in self.obj['questions']:
            if not isinstance(q, str):
                return False

        if ('notes' in self.obj and
            not isinstance(self.obj['notes'], str)):
            return False

        return True

    def valid_answerlist(self):
        if (not 'answers' in self.answers or
            not isinstance(self.answers['answers'], list)):
            return False

        if len(self.obj['questions']) != len(self.answers['answers']):
            return False

        for a in self.answers['answers']:
            if not isinstance(a, str):
                return False

        return True

    def valid(self):
        if (self.obj is None or
            not 'work_type' in self.obj or
            not isinstance(self.obj['work_type'], str) or
            not 'keywords' in self.obj or
            not isinstance(self.obj['keywords'], list)):
            return False

        for kw in self.obj['keywords']:
            if not isinstance(kw, str):
                return False

        wt = self.obj['work_type']
        if wt == 'image-question':
            return self.valid_questionlist()

        return False

    def answers_valid(self):
        if (self.answers is None or
            not 'work_type' in self.answers or
            not isinstance(self.answers['work_type'], str)):
            return False

        wt = self.answers['work_type']
        if wt == 'image-question':
            return self.valid_answerlist()

        return False

