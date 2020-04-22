class TemplateReader:
    def __init__(self):
        pass

    def read_course_template(self,cust_name):
        try:
            if (cust_name==True):
                email_file = open("email_templates/bot.html", "r")
                email_message = email_file.read()

            return email_message
        except Exception as e:
            print('The exception is '+str(e))
