from django_hosts import host, patterns

host_patterns = patterns(
    '',
    host(r'math', 'web.urls_math', name='math'),
    host(r'physics', 'web.urls_physics', name='physics'),
    host(r'junior', 'web.urls_junior', name='junior')
)
