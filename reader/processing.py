import re
from datetime import datetime

def country_code(data):
    for i in data:
        if i == 'Country0':
            global country_code
            try:
                data = data[i]
                indexes = re.search('Code', data)
                data = data[indexes.span()[1]+1:]
                data = re.findall('[A-Z]{3,3}', data)
                country_code = data[0]
            except:
                country_code = ''
        else:
            continue
    return country_code

def passport_no(data):
    for i in data:
        if i == 'Passport0':
            global passport_no
            try:
                data = data[i]
                indexes = re.search("No.", data)
                data = data[indexes.span()[1]+1:]
                data = re.sub('[a-z]', '', data)
                passport_no = re.findall("[A-Z0-9][ ]*[0-9]{6,9}", data)[0]
            except:
                passport_no = ''
        else:
            continue
    return passport_no

def surname(data):
    for i in data:
        if i == 'Surname0':
            global surname
            try:
                data = data[i]
                indexes = re.search('Surname', data)
                data = data[indexes.span()[1]+1:]
                data = re.sub('[a-z0-9/()]', '', data)
                lis = []
                for i in data.split(' '):
                    if len(i) > 3:
                        lis.append(i)
                    else:
                        pass
                surname = ' '.join(lis)
            except:
                surname = ''
        else:
            continue
    return surname

def given_name(data):
    for i in data:
        if i == 'Given0':
            global given_name
            try:
                data = data[i]
                indexes = re.search("Name", data)
                data = data[indexes.span()[1]+4:]
                data = re.sub('[a-z/]', '', data)
                x = data.split(' ')
                x1 = []
                for i in x:
                    if len(i) > 4:
                        x1.append(i)
                    else:
                        pass
                given_name = ' '.join(x1)
            except:
                given_name = ''
        else:
            continue
    return given_name

def nationality(data):
    for i in data:
        if i == 'Nationality0':
            global nationality
            try:
                data = data[i]
                indexes = re.search('Nationality', data)
                data = data[indexes.span()[1]+1:]
                data = re.sub('[a-z0-9/]', '', data)
                x = data.split(' ')
                for i in x:
                    if len(i) > 3:
                        nationality = i
                        break
            except:
                nationality = ''
        else:
            continue
    return nationality

def gender(data):
    for i in data:
        if i == 'Sex0':
            global gender
            try:
                data = data[i]
                data = re.sub('\W+', ' ', data)
                lis = data.split(' ')
                for i in lis:
                    if len(i) == 1:
                        if i.isupper():
                            gender = i
                    else:
                        pass
            except:
                gender = ''
        else:
            continue
    return gender

def date_of_birth(data):
    for i in data:
        if i == 'Date0':
            global dob
            try:
                dates = re.findall("[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}", data[i])
                fdates = [datetime.strptime(d, "%d/%m/%Y") for d in dates]
                fdates.sort()
                dob = [f.strftime("%d-%m-%Y") for f in fdates][0]
            except:
                dob = ''
        else:
            continue
    return dob

def place_of_birth(data):
    for i in data:
        if i == 'Birth1':
            global placeOfBirth
            try:
                data = data[i]
                # Finding multiple indexes for multiple occurences of the word 'Birth'
                result = [i.start() for i in re.finditer('Birth', data)]
                data = data[result[-1]:]
                indexes = re.search('Birth', data)
                # Slicing the string from last occuerence of 'Birth'
                data = data[indexes.span()[1]+1:]
                # Removing all smallcase words from the string
                placeOfBirth = re.sub('[a-z]', '', data)
            except:
                placeOfBirth = ''
        else:
            continue
    return placeOfBirth

def place_of_issue(data):
    for i in data:
        if i == 'Issue0':
            global place_of_issue
            try:
                data = data[i]
                # print("data")
                # print(data)
                index = re.search("Issue", data)
                # Slicing the sentence till Issue word
                data = data[index.span()[1]+1:]
                place_of_issue = re.sub('[a-z]', '', data)
                place_of_issue = re.findall("[A-Z]{3,30}", place_of_issue)[0]
            except:
                place_of_issue = ''
        else:
            continue
    return place_of_issue

def date_of_issue(data):
    for i in data:
        if i == 'Date1':
            global doi
            try:
                dates = re.findall("[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}", data[i])
                fdates = [datetime.strptime(d, "%d/%m/%Y") for d in dates]
                fdates.sort()
                doi, doe = [f.strftime("%d-%m-%Y") for f in fdates]
            except:
                doi = ''
        else:
            continue
    return doi

def date_of_expiry(data):
    for i in data:
        if i == 'Date1':
            global doe
            try:
                dates = re.findall("[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}", data[i])
                fdates = [datetime.strptime(d, "%d/%m/%Y") for d in dates]
                fdates.sort()
                doi, doe = [f.strftime("%d-%m-%Y") for f in fdates]
            except:
                doe = ''
        else:
            continue
    return doe
