from fiistudentrest.models import Student
from fiistudentrest.models import Professor
from fiistudentrest.api_functions.auth import verify_token
from fiistudentrest.utils.mail import send_mail

import hug


def exists(email, user_type):
    """ Verify if the user exists in the datastore """
    result = False
    query = user_type.query()
    query.add_filter('email', '=', email)
    print(query)
    query_it = query.fetch()
    for ent in query_it:
        if ent is None:
            print('The user is not in our database.')
            result = False
        else:
            print('The user exists in our database.')
            result = True
    return result


@hug.local()
@hug.get()
@hug.cli()
def quickmail(request, urlsafe: hug.types.text, subject: hug.types.text, content: hug.types.text):
    """Sends an email from a student to a professor"""
    authorization = request.get_header('Authorization')
    if not authorization:
        return {'status': 'error',
                'errors': [
                    {'for': 'request_header', 'message': 'No Authorization field exists in request header'}]}

    user_urlsafe = verify_token(authorization)
    if not user_urlsafe:
        return {'status': 'error',
                'errors': [
                    {'for': 'request_header', 'message': 'Header contains token, but it is not a valid one.'}]}

    student = Student.get(user_urlsafe)
    if not student:
        from_email = ""
    else: 
        from_email = student.email

    professor = Professor.get(urlsafe)
    if exists(from_email, Student) == True and exists(professor.email, Professor) == True:
        send_mail(from_email, professor.email, subject, content)
        return {'status': 'ok', 'errors': []}
    elif exists(from_email, Student) == True and exists(professor.email, Professor) == False:
        return {'status': 'error',
                'errors': [
                    {'for': 'email_professor', 'message': 'We could not find the professor with the email({}).'.format(professor.email)}]}
    elif exists(from_email, Student) == False and exists(professor.email, Professor) == True:
        return {'status': 'error',
                'errors': [
                    {'for': 'email_student', 'message': 'We could not find the student with the email({}).'.format(from_email)}]}
    else:
        return {'status': 'error', 'errors': [
            {'for': 'email_student', 'message': 'We could not find the student with the email({}).'.format(from_email)},
            {'for': 'email_professor', 'message': 'We could not find the professor with the email({}).'.format(professor.email)}]}


if __name__ == '__main__':
    quickmail.interface.cli()
