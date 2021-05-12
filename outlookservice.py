
"""
all of our Outlook API functions are implemented in this file
"""

import requests
import uuid
import json

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Generic API Sending
def make_api_call(method, url, token, user_email, payload = None, parameters = None):
  # Send these headers with all API calls
  headers = { 'User-Agent' : 'dcore-connection/1.0',
              'Authorization' : 'Bearer {0}'.format(token),
              'Accept' : 'application/json',
              'X-AnchorMailbox' : user_email }

  # Use these headers to instrument calls. Makes it easier
  # to correlate requests and responses in case of problems
  # and is a recommended best practice.
  request_id = str(uuid.uuid4())
  instrumentation = { 'client-request-id' : request_id,
                      'return-client-request-id' : 'true' }

  headers.update(instrumentation)

  response = None

  if (method.upper() == 'GET'):
      response = requests.get(url, headers = headers, params = parameters)
  elif (method.upper() == 'DELETE'):
      response = requests.delete(url, headers = headers, params = parameters)
  elif (method.upper() == 'PATCH'):
      headers.update({ 'Content-Type' : 'application/json' })
      response = requests.patch(url, headers = headers, data = json.dumps(payload), params = parameters)
  elif (method.upper() == 'POST'):
      headers.update({ 'Content-Type' : 'application/json' })
      response = requests.post(url, headers = headers, data = json.dumps(payload), params = parameters)

  return response
  
  
def get_me(access_token):
  get_me_url = graph_endpoint.format('/me')

  # Use OData query parameters to control the results
  #  - Only return the displayName and mail fields
  query_parameters = {'$select': 'displayName,mail'}

  r = make_api_call('GET', get_me_url, access_token, "", parameters = query_parameters)

  if (r.status_code == requests.codes.ok):
    return r.json()
  else:
    return "{0}: {1}".format(r.status_code, r.text)
    
    
def send_message(access_token,user_email, payload):
     get_messages_url = graph_endpoint.format('/Me/sendmail')      

     r = make_api_call('POST', 
                        get_messages_url, 
                        access_token, 
                        user_email, 
                        payload = payload,
                        )
     if (r.status_code == requests.codes.ok):
        print(r.json())
        return r.json()
     else:
        return "{0}: {1}".format(r.status_code, r.text)  