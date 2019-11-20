# Generated by Django 2.2.7 on 2019-11-18 10:30

from django.db import migrations


def fill_new_contact_field(apps, schema_editor):
    Aid = apps.get_model('aids', 'Aid')
    aids = Aid.objects.all()
    for aid in aids:
        contact_elts = []
        if aid.contact_detail:
            contact_elts.append('Nom / prénom : {}'.format(aid.contact_detail))

        if aid.contact_email:
            contact_elts.append('E-mail : {}'.format(aid.contact_email))

        if aid.contact_phone:
            contact_elts.append('Téléphone : {}'.format(aid.contact_phone))

        contact = '\n'.join(contact_elts)
        aid.contact = contact
        aid.save()


class Migration(migrations.Migration):

    dependencies = [
        ('aids', '0086_aid_contact'),
    ]

    operations = [
        migrations.RunPython(fill_new_contact_field, migrations.RunPython.noop)
    ]
