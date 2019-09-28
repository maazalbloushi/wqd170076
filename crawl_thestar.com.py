from lxml import html
import requests
import re
import calendar
import json
import time
import os

# importing necesscery libraries and tools

class Appcrawler:

    def __init__(self, starting_url):
        self.starting_url = starting_url


    '''[summary]
    # * This is a caller 
    Returns:
        [type] -- [description]
        [crawler_main_cats, Dictionary] -- [extracts main catagories from link]
    '''
    def crawl_cat(self):
        crawler_main_cats = self.get_cat_from_link(self.starting_url)

        return crawler_main_cats


    '''[summary]
    # * extracts main catagories from link put it in the root of a dictionary
    Returns:
        [type] -- [description]
        [cat_category] -- [Dictionary] --

        cat_category = {'Main Market' = ['Health Care'], ...}
    '''
    def get_cat_from_link(self, input_link):
        cat_category = {}

        start_page = requests.get(input_link)
        tree = html.fromstring(start_page.text)

        name = tree.xpath('//tr')

        for i in range(0, 5):
            # * First element is the name of category
            # * last character is ':' so we just ignore it

            cat_category[str(i+1) + '-' + name[i][0].text_content()[:-1]] = []

            # * Other elements are the sub-categories in different columns
            # * In D resolution(desktop) we have 3 columns of sub-categories(check the page please)
            # * We need to iterate through all 3 columns to catch all sub-categories

            # * I want to add str(i+1) in the beginning of each main category because
            # * I use dictionary and it is sortless. It means everytime I run dict.keys(), it
            # * may show something different. So it can't be used fo furthur tasks because
            # * they need some kind of same input for iteration
            for j in range(1, len(name[i])):
                for k in range(0, len(name[i][j])):
                    if str(name[i][j][k].text_content()) == 'Finance Services':
                        cat_category[str(i+1) + '-' + name[i][0].text_content()[:-1]].append('Financial Services')
                    else:
                        cat_category[str(i+1) + '-' + name[i][0].text_content()[:-1]].append(name[i][j][k].text_content())

        return cat_category


    '''[info]
    # * this is a caller
    Returns:
        [type] -- [description]
    '''
    def crawl_id_of_cat(self, input_main_categories):
        
        temp_list = self.get_cleaned_input_from_link(self.starting_url)

        crawled_ids = self.find_id_of_cat(temp_list, input_main_categories)

        return crawled_ids



    '''[info]
    # * Cleans the content of url given
    Returns:
        [type] -- [description]
        [cleaned_list] -- [List of lines]
    '''
    def get_cleaned_input_from_link(self,input_link):

        start_page = requests.get(input_link)
        tree = html.fromstring(start_page.text)

        start_of = tree.text_content().index('function loadSector()')
        end_of = tree.text_content().index('$(document).ready(function()')

        # * Cleaning up the input so it can easily converted to a list
        my_string = tree.text_content()[start_of:end_of]
        my_string = my_string.replace('else if', 'if')
        my_string = re.sub(r'\s{1,}?(if)', '\nif', my_string)
        my_string = re.sub(r'\s{1,}?(window)', '\nwindow', my_string)
        my_string = re.sub(r'\s{1,}?({)', '', my_string)
        my_string = re.sub(r'\s{1,}?(})', '', my_string)
        my_string = my_string[my_string.index('if ('):]
        my_string = re.sub(r'\s{1,}?(else)', '\nelse', my_string)
        my_string = my_string[:my_string.index('else')]
        my_string = my_string.replace('";\n', '')

        cleaned_list = my_string.split('if ')

        return cleaned_list



    '''[info]
    # * Each sub-category has its own id in html code that is not exactly similar to its name.
    # * .i.e. : (boardropval == "1" && sectdropval == "Health Care") -> id = main_healthcare
    # * This function will extract and add relevant id of each sub-category
    Returns:
        [type] -- [description]
        [output_main_categories] -- [Dictionary] --

        output_main_categories = {'Main Market' = ['Health Care', 'main_healthcare'], ...}
    '''
    def find_id_of_cat(self, input_list, input_main_categories):

        keys = list(input_main_categories.keys())

        # * The first element is '\n' so I just ignore it
        # * We need to iterate in whole dictionary to extract id of each element
        for i in range(1, len(input_list)):
            for j in range(0, len(keys)):
                # * The first value between " " is 'boardropval' which is the main category
                first = self.find_nth(input_list[i], '"', 1)
                second = self.find_nth(input_list[i], '"', 2)

                # * The second value between " " is 'sectdropval' which is the sub-category
                third = self.find_nth(input_list[i], '"', 3)
                forth = self.find_nth(input_list[i], '"', 4)

                # * The first condition will check the main category
                if (input_list[i][first+1:second] == keys[j][:1]):
                    for k in range(0, len(input_main_categories[keys[j]])):
                        # * The second condition will check the sub-category and append it to the dictionary
                        if (input_list[i][third+1:forth] == input_main_categories[keys[j]][k]):
                            input_main_categories[keys[j]][k]  = [input_main_categories[keys[j]][k], input_list[i][(self.find_nth(input_list[i], '?sector=', 1) + 8):]]


        output_main_categories = input_main_categories

        return output_main_categories




    '''[info]
    # * this is a caller
    Returns:
        [type] -- [description]
    '''
    def crawl_url(self, input_dict):
        temp_list = self.get_cleaned_input_from_link2(self.starting_url)

        crawled_urls = self.find_url_based_on_id(temp_list, input_dict)

        final_dict = self.crawl_company_names(crawled_urls)
        
        final_dict_values = self.crawl_values(final_dict)

        
        # !self.extract_values(final_dict_values)

        return final_dict_values


    '''[info]
    # * Cleans the content of url given
    Returns:
        [type] -- [description]
        [cleaned_list] -- [List of lines]
    '''
    def get_cleaned_input_from_link2(self,input_link):

        start_page = requests.get(input_link)
        tree = html.fromstring(start_page.text)

        start_of = tree.text_content().index('if (sect != null) switch (sect) {')
        end_of = tree.text_content().index('} function getUrlSector()')

        # * Cleaning up the input so it can easily converted to a list
        my_string = tree.text_content()[start_of:end_of]
        my_string = my_string[self.find_nth(my_string, 'case', 1):]
        my_string = my_string.replace('break; ', '')


        cleaned_list = my_string.split('case ')

        return cleaned_list



    '''[info]
    # * Each sub-category has its own id in html code that is not exactly similar to its name.
    # * .i.e. : (boardropval == "1" && sectdropval == "Health Care") -> id = main_healthcare
    # * Based on each id we can extract the relevant url to each id
    # * This function will extract and add relevant url of each id
    Returns:
        [type] -- [description]
        [output_dict] -- [Dictionary] --

        output_dict = {'Main Market' = ['Health Care', 'main_healthcare', 'url'], ...}
    '''
    def find_url_based_on_id(self, input_list, input_dict):

        keys = list(input_dict.keys())

        # * The first element is '\n' so I just ignore it
        # * We need to iterate in whole dictionary to extract url of each id
        for i in range(1, len(input_list)):
            for j in range(0, len(keys)):

                for k in range(0, len(input_dict[keys[j]])):
                    # * The first value between " " is 'id'
                    first = self.find_nth(input_list[i], '"', 1)
                    second = self.find_nth(input_list[i], '"', 2)

                    # * The third value between " " is the relevant url
                    fifth = self.find_nth(input_list[i], '"', 5)
                    sixth = self.find_nth(input_list[i], '"', 6)

                    # * The condition will check the sector id and append it to the dictionary
                    # * This url can be used to reach a new file to extract the name of the companies
                    # * related to each sub-category
                    if (input_list[i][first+1:second] == input_dict[keys[j]][k][1]):
                        input_dict[keys[j]][k].append(input_list[i][fifth+1:sixth])

        output_dict = input_dict
        return output_dict



    '''[info]
    # * The input url is like a dictionary. Each company has different items. Also the
    # * the name of each company is in front of 'counter'
    # * .i.e. "counter" = "ADVENTA"
    # * This function will extract the name of the companies
    Returns:
        [type] -- [description]
        [output_dict] -- [Dictionary] --

        output_dict
        = {'Main Market' = ['Health Care', 'main_healthcare', 'url',[ADVENTA, ...]], ...}
    '''
    def crawl_company_names(self, input_dict):

        keys = list(input_dict.keys())


        for i in range(0, len(keys)):
            for j in range(0, len(input_dict[keys[i]])):
                start_page = requests.get(input_dict[keys[i]][j][2])
                tree = html.fromstring(start_page.text)

                start_of = self.find_nth(tree.text_content(), '[', 1)
                end_of = self.find_nth(tree.text_content(), ']', 1)

                my_string = tree.text_content()[start_of+1:end_of]

                k = 1
                list_of_company_names = []

                index_of_counter = self.find_nth(my_string, '"counter"', 1)
                index_of_open = self.find_nth(my_string, '"open"', 1)

                while index_of_counter != -1:
                    temp_string = my_string[index_of_counter:index_of_open]
                    company_name = temp_string[self.find_nth(temp_string, '"', 3)+1 : self.find_nth(temp_string, '"', 4)]

                    list_of_company_names.append(company_name)

                    k+=1
                    index_of_counter = self.find_nth(my_string, '"counter"', k)
                    index_of_open = self.find_nth(my_string, '"open"', k)

                input_dict[keys[i]][j].append(list_of_company_names)


        output_dict = input_dict
        return output_dict



    '''[info]
    # * Based on the name of each company, we can extract the url related to each one.
    # * This function will save the raw content of page related to each company that
    # * contains the values between the dates indicated at the end of each url.
    Returns:
        [type] -- [description]
        [output_dict] -- [Dictionary] --

        output_dict
        = {'[Main Market]' = ['Health Care', 'main_healthcare', 'url',
        [[ADVENTA, 'whole content of page'], ...]], ...}
    '''
    def crawl_values(self,input_dict):

        keys = list(input_dict.keys())
        end_time = calendar.timegm(time.gmtime())

        for i in range(0, len(keys)):
            for j in range(0, len(input_dict[keys[i]])):#6433930
                for k in range(0, len(input_dict[keys[i]][j][3])):
                    final_js = 'https://charts.thestar.com.my/datafeed-udf/history?symbol=' + input_dict[keys[i]][j][3][k] + '&resolution=D&from=1388538061&to=' + str(end_time)

                    start_page = requests.get(final_js)
                    tree = html.fromstring(start_page.text)

                    input_dict[keys[i]][j][3][k] = [input_dict[keys[i]][j][3][k], tree.text_content()]

        output_dict = input_dict
        return output_dict


    '''[info]
    # * The content of each page is [t(time), c(close), o(open), h(high), l(low), v(volume), s(status)]
    # * This function will extract these values
    Returns:
        [type] -- [description]
        [output_dict] -- [Dictionary] --

        output_dict
        = {'Main Market' = ['Health Care', 'main_healthcare', 'url',
        [[ADVENTA, [t, c, o, h, l, v], ...]], ...}
    '''
    def extract_values(self, input_dict):

        my_list = []

        keys = list(input_dict.keys())

        for i in range(0, len(keys)):
            for j in range(0, len(input_dict[keys[i]])):
                for k in range(0, len(input_dict[keys[i]][j][3])):
                    input_string = input_dict[keys[i]][j][3][k][0]

                    my_list.append(input_string[self.find_nth(input_string, '[', 1)+1:self.find_nth(input_string, ']', 1)])
                    my_list.append(input_string[self.find_nth(input_string, '[', 2)+1:self.find_nth(input_string, ']', 2)])
                    my_list.append(input_string[self.find_nth(input_string, '[', 3)+1:self.find_nth(input_string, ']', 3)])
                    my_list.append(input_string[self.find_nth(input_string, '[', 4)+1:self.find_nth(input_string, ']', 4)])
                    my_list.append(input_string[self.find_nth(input_string, '[', 5)+1:self.find_nth(input_string, ']', 5)])
                    my_list.append(input_string[self.find_nth(input_string, '[', 6)+1:self.find_nth(input_string, ']', 6)])

                    # * To convert the time to a human-readable format
                    my_time = []
                    my_split = my_list[0].split(',')
                    for i in range(0, len(my_split)):
                        my_time.append(time.strftime('%Y-%m-%d', time.localtime(int(my_split[i]))))

                    my_list[0] = my_time

        output_list = my_list
        return output_list


    '''[info]
    # * This function will return the index of nth occurance of 'what_to_find' in 'input_string'
    Returns:
        [type] -- [description]
        [start] -- [index of nth occurance of 'what_to_find' in 'input_string']
    '''
    def find_nth(self, input_string, what_to_find, n):
        start = input_string.find(what_to_find)

        while start>= 0 and n > 1:
            start = input_string.find(what_to_find, start+len(what_to_find))
            n -= 1

        return start


    '''[info]
    # * This function will export the input_dict as final output for analysis to a 'data.json' file
    '''
    def export_json_file(self, input_dict):
        
        with open(str(time.strftime('%Y%m%d', time.gmtime())) +'.json', 'w') as outfile:
            json.dump(input_dict, outfile)


    '''[info]
    # * This function will open the .json file saved using the same script
    Returns:S
        [type] -- [description]
        [dictdump] -- [a dictionary contains whole the extracted data using same script]
    '''

    def import_json_file(self, input_dict):
        with open('crawl_thestar.com.json', 'w') as handle:
            dictdump = json.loads(handle.read())
        return dictdump


class App:

    #* Return the main and sub-categories
    crawler = Appcrawler('https://s3-ap-southeast-1.amazonaws.com/biz.thestar.com.my/layout_v2/sector_stock.js')
    app_main_categories = crawler.crawl_cat()


    #* Return the html id related to each sub-categories
    crawler = Appcrawler('https://s3-ap-southeast-1.amazonaws.com/biz.thestar.com.my/layout/stocks/loadsec.js')
    app_dict_sub_category_based_on_id = crawler.crawl_id_of_cat(app_main_categories)

    #* Return a dict contains whole the data we are looking for
    crawler = Appcrawler('https://s3-ap-southeast-1.amazonaws.com/biz.thestar.com.my/layout/stocks/data.js')
    app_dict_of_companies_based_on_sub_category = crawler.crawl_url(app_dict_sub_category_based_on_id)

    #* It can export the dict contains whole the data we are looking for
    crawler.export_json_file(app_dict_of_companies_based_on_sub_category)