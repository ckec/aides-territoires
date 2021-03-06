from functools import reduce
from operator import and_

from django.db.models import Q
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


from core.admin import InputFilter
from aids.admin_views import AmendmentMerge
from aids.models import Aid
from aids.forms import AidAdminForm


class LiveAidListFilter(admin.SimpleListFilter):
    """Custom admin filter to target aids with various statuses."""

    title = _('Display status')
    parameter_name = 'displayed'

    def lookups(self, request, model_admin):
        return (
            ('open', _('Open aids')),
            ('expired', _('Expired aids')),
            ('deadline', _('Deadline approaching')),
            ('hidden', _('Currently not displayed')),
            ('live', _('Currently displayed')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'open':
            return queryset.open()

        if self.value() == 'expired':
            return queryset.expired()

        if self.value() == 'deadline':
            return queryset.soon_expiring()

        if self.value() == 'hidden':
            return queryset.hidden()

        if self.value() == 'live':
            return queryset.published().open()


class AuthorFilter(InputFilter):
    parameter_name = 'author'
    title = _('Author')

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:

            return queryset.filter(Q(author__full_name__icontains=value))


class BackersFilter(InputFilter):
    parameter_name = 'backers'
    title = _('Backers')

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            bits = value.split(' ')
            financer_filters = [
                Q(financers__name__icontains=bit)
                for bit in bits
            ]
            instructor_filters = [
                Q(instructors__name__icontains=bit)
                for bit in bits
            ]

            return queryset.filter(
                Q(reduce(and_, financer_filters)) |
                Q(reduce(and_, instructor_filters)))


class PerimeterFilter(InputFilter):
    parameter_name = 'perimeter'
    title = _('Perimeter')

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:

            return queryset.filter(Q(perimeter__name__icontains=value))


class AidAdmin(admin.ModelAdmin):
    """Admin module for aids."""

    class Media:
        css = {
            'all': (
                '/static/css/admin.css',
                '/static/trumbowyg/dist/ui/trumbowyg.css',
            )
        }
        js = [
            'admin/js/jquery.init.js',
            '/static/js/plugins/softmaxlength.js',
            '/static/js/aids/enable_softmaxlength.js',
            '/static/trumbowyg/dist/trumbowyg.js',
            '/static/trumbowyg/dist/langs/fr.js',
            '/static/js/enable_rich_text_editor.js',
        ]

    form = AidAdminForm
    ordering = ['-id']
    save_as = True
    actions = ['make_mark_as_CFP']
    list_display = [
        'name', 'all_financers', 'all_instructors', 'author_name',
        'recurrence', 'date_updated', 'date_published', 'is_imported',
        'submission_deadline', 'status']
    autocomplete_fields = ['author', 'financers', 'instructors', 'perimeter']
    search_fields = ['name']
    list_filter = [
        'status', 'recurrence', 'is_imported', 'is_call_for_project',
        LiveAidListFilter, AuthorFilter, BackersFilter, PerimeterFilter]

    filter_vertical = ['categories']  # Overriden in the widget definition
    readonly_fields = [
        'is_imported', 'import_uniqueid', 'import_data_url',
        'import_share_licence', 'import_last_access', 'date_created',
        'date_updated', 'date_published']
    fieldsets = [
        (_('Aid presentation'), {
            'fields': (
                'name',
                'slug',
                'categories',
                'targeted_audiances',
                'financers',
                'financer_suggestion',
                'instructors',
                'instructor_suggestion',
                'author',
            )
        }),

        (_('Aid perimeter'), {
            'fields': (
                'perimeter',
            )
        }),

        (_('Aid calendar'), {
            'fields': (
                'recurrence',
                'start_date',
                'predeposit_date',
                'submission_deadline',
            )
        }),

        (_('Aid description'), {
            'fields': (
                'is_call_for_project',
                'aid_types',
                'subvention_rate',
                'subvention_comment',
                'mobilization_steps',
                'destinations',
                'description',
                'project_examples',
                'eligibility',
            )
        }),

        (_('Contact and actions'), {
            'fields': (
                'origin_url',
                'application_url',
                'contact',
            )
        }),

        (_('Aid admin'), {
            'fields': (
                'status',
            )
        }),

        (_('Import related data'), {
            'fields': (
                'is_imported',
                'import_uniqueid',
                'import_data_url',
                'import_share_licence',
                'import_last_access',
            )
        }),
        (_('Misc data'), {
            'fields': (
                'date_created',
                'date_updated',
                'date_published',
            )
        }),
    ]

    def get_queryset(self, request):
        qs = Aid.objects.all()
        qs = qs.prefetch_related('financers', 'instructors')
        qs = qs.select_related('author')
        return qs

    def author_name(self, aid):
        return aid.author.full_name
    author_name.short_description = _('Author')

    def all_financers(self, aid):
        financers = [backer.name for backer in aid.financers.all()]
        return ', '.join(financers)
    all_financers.short_description = _('Financers')

    def all_instructors(self, aid):
        instructors = [backer.name for backer in aid.instructors.all()]
        return ', '.join(instructors)
    all_instructors.short_description = _('Instructors')

    def make_mark_as_CFP(self, request, queryset):
        queryset.update(is_call_for_project=True)
        self.message_user(request, _('The selected aids were set as CFP'))
    make_mark_as_CFP.short_description = _('Set as CFP')


class Amendment(Aid):
    """We need this so we can register the same model twice."""
    class Meta:
        proxy = True
        verbose_name = _('Amendment')
        verbose_name_plural = _('Amendments')


class AmendmentChangeList(ChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        url = reverse('admin:aids_amendment_merge', args=[pk])
        return url


class AmendmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'amended_aid', 'amendment_author_name', 'date_created'
    ]

    def get_queryset(self, request):
        qs = Aid.amendments.all()
        qs = qs.prefetch_related('financers')
        qs = qs.select_related('author')
        return qs

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(_('<path:object_id>/merge/'), self.admin_site.admin_view(
                AmendmentMerge.as_view()), name='aids_amendment_merge'),
        ]
        return my_urls + urls

    def get_changelist(self, request, **kwargs):
        return AmendmentChangeList


admin.site.register(Aid, AidAdmin)
admin.site.register(Amendment, AmendmentAdmin)
