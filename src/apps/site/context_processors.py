import info


def site_info(request):
    return {
        'APP_NAME': info.NAME,
        'APP_VERSION': info.__version__
    }
