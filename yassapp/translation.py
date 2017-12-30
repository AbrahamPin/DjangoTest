from django.utils import translation


class TranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.GET.get('language', 'default')
        if language != 'default':
            request.session[translation.LANGUAGE_SESSION_KEY] = language
        try:
            language = request.session[translation.LANGUAGE_SESSION_KEY]
            if language != 'en':
                translation.activate(language)
        except KeyError:
            pass
        return self.get_response(request)
