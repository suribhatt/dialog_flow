from flask import Flask, request, make_response
import json
import os
#from flask_cors import cross_origin
from SendEmail.sendEmail import EmailSender
from logger import logger
from email_templates import template_reader
import  requests
app = Flask(__name__)


#geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
#@cross_origin
def webhook():

    req = request.get_json(silent=True, force=True)
    log = logger.Log()
    res = processRequest(req)

    res = json.dumps(res, indent=4)

    #print(res)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def get_api_data(cust_district,cust_city):
    log = logger.Log()
    if cust_city:
        api_url = 'https://api.covid19india.org/v2/state_district_wise.json'
    else:
        api_url = 'https://api.covid19api.com/summary'
    response = requests.get(api_url)
    status = False
    message = ''
    if response.status_code in [200, 201]:
        status = True
        content = response.content
        return_data = json.loads(content.decode('utf-8'))
        if cust_city:
            for i in return_data:
                if i.get('state','').lower()==cust_city.lower():
                    district_data = i.get('districtData')
                    if district_data:
                        if cust_district:
                            for imp_data in district_data:
                                if cust_district and cust_district.lower()==imp_data.get('district').lower():
                                    message += '''
                                    District Name:%s
                                    Active:%s
                                    
                                    deceased: %s
                                   ''' % (imp_data['district'], imp_data['active'],imp_data['deceased'])
                        else:
                            for imp_data in district_data:
                                message += '''District Name:%s
                                                           Active:%s
                                                           
                                                           deceased: %s
                                                           ''' % (
                                imp_data['district'], imp_data['active'],imp_data['deceased'])
        else:
            if return_data:


                global_information = return_data.get('Global',{})
                if global_information:
                    message +='''
                    Global Information:
                    NewConfirmed:%s,
                    TotalConfirmed:%s,
                    NewDeaths:%s,
                    TotalDeaths:%s,
                    NewRecovered:%s,
                    TotalRecovered:%s
                    '''%(
                        global_information['NewConfirmed'],
                        global_information['TotalConfirmed'],
                        global_information['NewDeaths'],
                        global_information['TotalDeaths'],
                        global_information['NewRecovered'],
                        global_information['TotalRecovered']
                    )
    return {'status':status, 'message':message}






def processRequest(req):

   log = logger.Log()

   sessionID = req.get('responseId')
   result = req.get("queryResult")
   user_says = result.get("queryText")
   log.write_log(sessionID, "User Says: "+user_says)
   parameters = result.get("parameters")
   #cust_name = parameters.get("name")
   #cust_contact = parameters.get("mobile")
   cust_email = parameters.get("mail")
   cust_city = parameters.get("state")
   custdistrict = parameters.get('district')
   intent = result.get("intent").get('displayName')
   message = 'No Data Found'
   api_data = get_api_data(custdistrict,cust_city)
   if api_data.get('status',False):
        message = api_data['message']
   log.write_log('cust', "Cust Details%r"%[cust_city, cust_email, custdistrict])

   if (intent== 'zip'):

       email_sender = EmailSender()
       #template = template_reader.TemplateReader()
       email_file = open("email_templates/bot.html", "r")
       email_message = email_file.read()
       #email_message = template.read_course_template(cust_name)
       email_sender.send_email_to_student(cust_email, email_message, message)
       #email_file_support = open("email_templates/support_team_Template.html", "r")
       #email_message_support = email_file_support.read()

       fulfillmentText = "We have sent the course syllabus "
       log.write_log('fulfillmentText', "Bot Says: " + fulfillmentText)

       return {
           "fulfillmentText": fulfillmentText
        }
   else:

        pass


if __name__ == '__main__':
    port = int(os.getenv('PORT', 80))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='127.0.0.1')
