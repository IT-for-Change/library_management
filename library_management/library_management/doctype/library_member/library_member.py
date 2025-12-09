# Copyright (c) 2025, ITFC and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils.jinja import render_template


class LibraryMember(Document):
    #this method will run every time a document is saved
    def before_save(self):
    
        template_path = "library_management/templates/odk_form.xml"
        context = {
            "title": f'{self.first_name}'
        }
        output = render_template(template_path, context)
        self.full_name = f'{self.first_name} {self.last_name or ""}'
    
        file_doc = frappe.get_doc({
	        "doctype": "File",
	        "file_name": f'{self.first_name}_form.xml',  # String that is your file's name
	        "attached_to_doctype": None,
	        "attached_to_name": None,
	        "is_private": True,
	        "content": output,  # Your text/data content goes here.
	        "folder": "Home"  #  If you want to save in subdirectory, enter 'Home/MySubdirectory'
	        }
        )
        file_doc.save()
        
        self.authorisation_letter = file_doc.file_url
