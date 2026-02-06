from django.utils import translation


class AdminEnglishMiddleware:
    """
    Forces Django Admin UI to English, independent of the public-site language.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        previous_language = translation.get_language()

        if request.path.startswith("/admin"):
            translation.activate("en")
            request.LANGUAGE_CODE = "en"

        response = self.get_response(request)

        # Restore previous language for the rest of the site
        if previous_language:
            translation.activate(previous_language)

        return response
