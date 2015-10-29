import json
import urllib, urllib2
from keys import *

BING_API_KEY = secret_bing_api_key

def run_query(search_terms):
    # specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'

    # specify how many results
    # offset specifies where results list starts from
    # results_per_page = 10 and offset = 11 would start from page 2
    results_per_page = 10
    offset = 0

    # wrap quotes around query terms
    # the query used will be stored in variable query
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    # construct latter part of request url
    # set response format to JSON and sets other properties
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url,
        source,
        results_per_page,
        offset,
        query)

    # setup authentication with Bing servers
    # the username must be a blank string, and put in your API key!
    username = ''


    # create a 'password manager' which handles authentication for us
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, BING_API_KEY)

    # create results list which we'll populate
    results = []

    try:
        # prepare for connecting to Bing's servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # connect to server and read response generated
        response = urllib2.urlopen(search_url).read()

        # convert string response to Python dict object
        json_response = json.loads(response)

        # loop through each returned page, populating results list
        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})

    # catch a URLError exception - something went wrong while connecting
    except urllib2.URLError, e:
        print "Error when querying the Bing API: ", e

    # for use with main() when testing via command line
    # print results

    # return list of results to the calling function
    return results

# for command line testing
# def main():
#     term = raw_input('Query terms? > ')
#     run_query(term)
#
# if __name__ == '__main__':
#     main()
