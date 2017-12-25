from django.utils import translation


class TranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if the user changed the language with the get form, we set the
        # session variable to this new language
        language = request.GET.get('language', 'default')
        if language != 'default':
            request.session[translation.LANGUAGE_SESSION_KEY] = language

        # if a language has been set and is not English, we activate the
        # translation
        try:
            language = request.session[translation.LANGUAGE_SESSION_KEY]
            if language != 'en':
                translation.activate(language)
        except KeyError:
            pass

        return self.get_response(request)
