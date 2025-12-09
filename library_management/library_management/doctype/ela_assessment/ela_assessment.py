# Copyright (c) 2025, ITFC and contributors
# For license information, please see license.txt

from datetime import datetime
import zoneinfo


# import frappe
from frappe.model.document import Document
import frappe
from frappe.utils.jinja import render_template
from frappe.utils import slug


class ELAAssessment(Document):

    def before_save(self):

        learner_list = frappe.get_all(
            'Learner',
            filters={'cohort': f'{self.cohort}'},
            fields=['name1', 'learner_id', 'cohort']
        )

        questions = self.assessment_questions
        text = ''
        for question in questions:
            text += f'{question.response_type} | {question.mandatory} | {question.question_prompt_rich_text}'

        activities = {}
        if (self.activity == None):
            activity_list = frappe.get_all(
                'ELA Activity', fields=['name', 'title'])
            for activity in activity_list:
                activities[activity.name] = activity.title
        else:
            activity = frappe.get_all('ELA Activity',
                                      filters={
                                          'name': self.activity},
                                      fields=['name', 'title']
                                      )
            activities[activity[0].name] = activity[0].title

        template_path = "library_management/templates/odk_form.xml"
        context = {
            "title": self.name,
            "cohort": self.cohort,
            "learners": str(learner_list),
            "questions": str(text),
            "activities": str(activities)
        }

        output = render_template(template_path, context)

        attachments = frappe.get_all('File', filters={
            'attached_to_doctype': 'ELA Assessment',
            'attached_to_name': self.name
        })

        if (len(attachments) > 0):
            form_file_old = frappe.delete_doc('File', attachments[0].name)

        file_name = slug(self.title).upper()

        file_doc = frappe.get_doc({
            "doctype": "File",
            # String that is your file's name
            "file_name": f'ELA-FORM-{file_name}.xml',
            "attached_to_doctype": 'ELA Assessment',
            "attached_to_name": self.name,
            "is_private": True,
            "content": output,  # Your text/data content goes here.
            "folder": "Home"  # If you want to save in subdirectory, enter 'Home/MySubdirectory'
        }
        )
        file_doc.save()

        current_time = datetime.now(
            zoneinfo.ZoneInfo("Asia/Kolkata")).strftime("%H:%M:%S")

        current_date = datetime.now(
            zoneinfo.ZoneInfo("Asia/Kolkata")).strftime("%d-%b-%Y")

        self.form_last_generated = f'Form last generated at {current_time} on {current_date}'
