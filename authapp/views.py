import json
import re
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import AlternativeEmail

ATTENDANCE_REASON_OPTIONS = {
    'Intensive study',
    'Transferred',
}

_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def _safe_identifier(value: str, label: str) -> str:
    if not value or not _IDENTIFIER_RE.match(value):
        raise ValueError(f'Invalid {label}: {value!r}')
    return connection.ops.quote_name(value)


def _resolve_column(schema_name: str, table_name: str, preferred: str, *, fallbacks=None, required=False):
    candidates = []
    if preferred:
        candidates.append(preferred)
    for item in (fallbacks or []):
        if item and item not in candidates:
            candidates.append(item)

    with connection.cursor() as cursor:
        for candidate in candidates:
            cursor.execute(
                '''
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s AND column_name = %s
                LIMIT 1
                ''',
                [schema_name, table_name, candidate],
            )
            if cursor.fetchone():
                return connection.ops.quote_name(candidate), candidate

    if required:
        raise ValueError(f'Column not found: {preferred!r}')
    return None, None


def _to_text(value):
    if value is None:
        return ''
    return str(value).strip()


def _to_int(value):
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _join_alternative_emails(primary_email: str, secondary_email: str) -> str:
    emails = []
    for value in (primary_email, secondary_email):
        text = _to_text(value)
        if text and text not in emails:
            emails.append(text)
    return ', '.join(emails)


def _get_group_options(schema: str, table: str, group_col: str):
    if not group_col:
        return []

    sql = (
        f"SELECT DISTINCT {group_col} "
        f"FROM {schema}.{table} "
        f"WHERE {group_col} IS NOT NULL AND TRIM(CAST({group_col} AS TEXT)) <> '' "
        f"ORDER BY {group_col} ASC"
    )

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    return [_to_text(row[0]) for row in rows if _to_text(row[0])]


def _client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip() or 'unknown'
    return request.META.get('REMOTE_ADDR', 'unknown')


def _cache_incr(key: str, timeout: int) -> int:
    if cache.add(key, 1, timeout=timeout):
        return 1
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=timeout)
        return 1


def _is_rate_limited(request, email: str) -> bool:
    ip = _client_ip(request)
    normalized_email = email.lower()
    window = max(1, int(getattr(settings, 'LOGIN_RATE_LIMIT_WINDOW_SECONDS', 300)))
    per_ip = max(1, int(getattr(settings, 'LOGIN_RATE_LIMIT_PER_IP', 30)))
    per_email = max(1, int(getattr(settings, 'LOGIN_RATE_LIMIT_PER_EMAIL', 8)))
    block_seconds = max(1, int(getattr(settings, 'LOGIN_BLOCK_SECONDS', 900)))

    ip_block_key = f'login:block:ip:{ip}'
    email_block_key = f'login:block:email:{normalized_email}'
    if cache.get(ip_block_key) or cache.get(email_block_key):
        return True

    ip_count = _cache_incr(f'login:count:ip:{ip}', timeout=window)
    email_count = _cache_incr(f'login:count:email:{normalized_email}', timeout=window)

    limited = False
    if ip_count > per_ip:
        cache.set(ip_block_key, 1, timeout=block_seconds)
        limited = True
    if email_count > per_email:
        cache.set(email_block_key, 1, timeout=block_seconds)
        limited = True

    return limited


@ensure_csrf_cookie
def login_page(request):
    return render(request, 'login.html')


def favicon(request):
    templates_dir = Path(settings.BASE_DIR) / 'templates'
    for name in ('icon.png', 'images.png'):
        icon_path = templates_dir / name
        if icon_path.exists():
            return FileResponse(open(icon_path, 'rb'), content_type='image/png')
    raise Http404('Icon not found')


def healthz(request):
    return JsonResponse({'status': 'ok'})


@require_POST
def student_login(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    email = (payload.get('email') or '').strip()
    nickname = _to_text(payload.get('nickname'))
    alternative_email = _to_text(payload.get('alternative_email'))
    alternative_email_2 = _to_text(payload.get('alternative_email_2'))
    attendance_group = _to_text(payload.get('attendance_group'))
    attendance_reason = _to_text(payload.get('attendance_reason'))
    if not email:
        return JsonResponse({'detail': 'Please enter your Aptem email'}, status=400)
    if _is_rate_limited(request, email):
        return JsonResponse(
            {'detail': 'Too many attempts. Please try again later.'},
            status=429,
        )

    schema_name = settings.KBC_TABLE_SCHEMA
    table_name = settings.KBC_TABLE_NAME

    try:
        schema = _safe_identifier(schema_name, 'schema name')
        table = _safe_identifier(table_name, 'table name')

        email_col, _ = _resolve_column(
            schema_name,
            table_name,
            settings.KBC_EMAIL_COLUMN,
            required=True,
        )
        id_col, _ = _resolve_column(
            schema_name,
            table_name,
            getattr(settings, 'KBC_ID_COLUMN', 'ID'),
            fallbacks=['ID', 'id'],
            required=True,
        )
        name_col, _ = _resolve_column(
            schema_name,
            table_name,
            getattr(settings, 'KBC_NAME_COLUMN', 'FullName'),
            fallbacks=['FullName', 'FirstName'],
            required=False,
        )
        group_col, _ = _resolve_column(
            schema_name,
            table_name,
            getattr(settings, 'KBC_GROUP_COLUMN', 'Group'),
            fallbacks=['Group', 'Program Name'],
            required=False,
        )
    except ValueError:
        return JsonResponse({'detail': 'Server configuration error'}, status=500)

    select_fields = ['1 AS ok']
    select_fields.append(f'{id_col} AS student_id')
    if name_col:
        select_fields.append(f'{name_col} AS student_name')
    if group_col:
        select_fields.append(f'{group_col} AS student_group')

    sql = (
        f"SELECT {', '.join(select_fields)} "
        f"FROM {schema}.{table} "
        f"WHERE LOWER({email_col}) = LOWER(%s) "
        "LIMIT 1"
    )

    with connection.cursor() as cursor:
        cursor.execute(sql, [email])
        row = cursor.fetchone()
        if row is None:
            return JsonResponse({'ok': False, 'detail': 'Please enter your Aptem email'}, status=401)
        columns = [col[0] for col in cursor.description]

    row_data = dict(zip(columns, row))
    group_options = _get_group_options(schema, table, group_col) if group_col else []
    current_group = _to_text(row_data.get('student_group'))

    if not nickname or not alternative_email:
        return JsonResponse(
            {
                'ok': False,
                'detail': 'Please add your nickname and the alternative email address you use.',
                'requires_additional_details': True,
                'name': _to_text(row_data.get('student_name')),
                'group': current_group,
                'group_options': group_options,
            },
            status=400,
        )
    if alternative_email_2 and alternative_email_2 == alternative_email:
        return JsonResponse({'detail': 'Please enter a different second alternative email.'}, status=400)

    if attendance_group and attendance_group not in group_options:
        return JsonResponse({'detail': 'Please choose a valid group.'}, status=400)
    if attendance_group and attendance_reason not in ATTENDANCE_REASON_OPTIONS:
        return JsonResponse({'detail': 'Please choose a valid reason.'}, status=400)
    if not attendance_group:
        attendance_reason = ''

    response_data = {'ok': True, 'message': 'Your details have been saved successfully.'}
    student_id = _to_int(row_data.get('student_id'))
    student_name = _to_text(row_data.get('student_name'))
    student_group = _to_text(row_data.get('student_group'))

    if student_id is None:
        return JsonResponse({'detail': 'Student ID is missing or invalid in source table.'}, status=500)

    combined_alternative_email = _join_alternative_emails(alternative_email, alternative_email_2)

    record_defaults = {
        'aptem_name': student_name,
        'group': student_group,
        'attendance_group': attendance_group,
        'attendance_reason': attendance_reason,
        'aptem_email': email,
        'nickname': nickname,
        'alternative_email': combined_alternative_email,
        'alternative_email_2': '',
    }

    AlternativeEmail.objects.update_or_create(
        student_id=student_id,
        defaults=record_defaults,
    )

    response_data['name'] = student_name
    response_data['group'] = student_group
    response_data['group_options'] = group_options

    return JsonResponse(response_data)

