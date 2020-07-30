import datetime


from django.core.management.base import BaseCommand

from bellettrie_library_system.settings import OLD_DB, OLD_PWD, OLD_USN
from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork, Item, NamedTranslatableThing


def round_number(number: int):
    return int(number * 10) / 10


def fill_name(thing: NamedTranslatableThing, data):
    thing.title = data.get("titel")
    thing.article = data.get("lidwoord")
    thing.sub_title = data.get("subtitel")
    thing.language = data.get("taal")
    thing.is_translated = data.get("is_vertaald")
    thing.original_article = data.get("orig_lidwoord")
    thing.original_title = data.get("orig_titel")
    thing.original_subtitle = data.get("orig_subtitel")
    thing.original_language = data.get("orig_taal")


def fill_data(thing: NamedTranslatableThing, data):
    fill_name(thing, data)
    thing.hidden = data.get("verbergen")
    thing.save()


class Command(BaseCommand):
    help = '0 for only publications, 1 for extras, 2 for everything. -1 for reload names etc.'

    def add_arguments(self, parser):
        parser.add_argument('everything', nargs='+', type=int)

    @staticmethod
    def handle_publication(publication_id, tree, finder):
        data = finder.get(publication_id)
        publication = None
        if len(Publication.objects.filter(old_id=publication_id)):
            publication = Publication.objects.get(old_id=publication_id)
        else:
            publication = Publication(
                date_added=data.get("gecatalogiseerd") or datetime.datetime.today(),
                comment=data.get("commentaar"),
                internal_comment=data.get("intern_commentaar"),
                signature_fragment=data.get("signatuurfragment"),
                old_id=publication_id)
        fill_data(publication, data)

    @staticmethod
    def handle_subwork(sub_work, tree, finder):
        data = finder.get(sub_work)
        work = SubWork(date_added=data.get("gecatalogiseerd") or datetime.datetime.today(),
                       comment=data.get("commentaar"),
                       internal_comment=data.get("intern_commentaar"),
                       signature_fragment=data.get("signatuurfragment"),
                       old_id=sub_work)
        fill_data(work, data)
        pub = Publication.objects.get(old_id=tree.get(sub_work))
        WorkInPublication.objects.create(work=work,
                                         publication=pub,
                                         number_in_publication=round_number(data.get("reeks_deelnummer")),
                                         display_number_in_publication=data.get("reeks_deelaanduiding"))

    @staticmethod
    def handle_series_node(handled, node, tree, finder, duds):
        if node in handled:
            return []
        data = finder.get(node)
        my_num = round_number(data.get("reeks_deelnummer"))

        handled_list = []
        nr = finder.get(node).get("reeks_publicatienummer")

        if nr > 0:
            handled_list += Command.handle_series_node(handled, nr, tree, finder, duds)
        if my_num == 0:
            if nr > 0:
                print(str(data.get("reeks_publicatienummer")) + ": 0 to None")
            my_num = None
        if my_num is not None and duds[data.get("reeks_publicatienummer"), round_number(data.get("reeks_deelnummer"))] > 1:
            print(str(data.get("reeks_publicatienummer")) + ": Double part for number " + str(data.get("reeks_deelnummer")) + " (after rounding down)")
            my_num = None
        if data.get("reeks_publicatienummer") > 0:
            super_series = Series.objects.get(old_id=data.get("reeks_publicatienummer"))
            Series.objects.create(part_of_series=super_series, number=my_num,
                                  display_number=data.get(
                                      "reeks_deelaanduiding"), old_id=node, is_translated=False,
                                  language=data.get('taal'),
                                  signature_fragment=data.get("signatuurfragment"))
        else:
            Series.objects.create(number=my_num,
                                  display_number=data.get(
                                      "reeks_deelaanduiding"), old_id=node, is_translated=False,
                                  language=data.get('taal'),
                                  signature_fragment=data.get("signatuurfragment"))

        handled_list.append(node)

        return handled_list

    @staticmethod
    def handle_part_of_series(publication, tree, finder, duds):
        data = finder.get(publication)
        pub = data.get("reeks_publicatienummer")
        series_data = finder.get(pub)
        if series_data.get("type") != 1:
            return
        ser = Series.objects.get(old_id=pub)
        work = Work.objects.get(old_id=publication)
        nr = round_number(data.get("reeks_deelnummer"))

        if nr == 0:
            if pub > 0:
                print(str(data.get("reeks_publicatienummer")) + ": 0 to None")
            nr = None
        if nr is not None and duds[data.get("reeks_publicatienummer"), round_number(data.get("reeks_deelnummer"))] > 1:
            print(str(data.get("reeks_publicatienummer")) + ": Double part for number " + str(data.get("reeks_deelnummer")) + " (after rounding down)")
            nr = None
        WorkInSeries.objects.create(part_of_series=ser, old_id=publication, work=work,
                                    number=nr,
                                    display_number=data.get(
                                        "reeks_deelaanduiding"))

    def handle(self, *args, **options):
        opt = (options['everything'][0])

        from bellettrie_library_system.settings_migration import migration_database
        mycursor = migration_database.cursor(dictionary=True)

        tree = dict()
        finder = dict()
        mycursor.execute("SELECT * FROM publicatie where verbergen = 0")
        duds = dict()

        count = 0
        for x in mycursor:
            if x.get("reeks_publicatienummer") > 0:
                tree[x.get("publicatienummer")] = x.get("reeks_publicatienummer")
                countz = duds.get((x.get("reeks_publicatienummer"), round_number(x.get("reeks_deelnummer"))), 0)
                duds[(x.get("reeks_publicatienummer"), round_number(x.get("reeks_deelnummer")))] = countz + 1
                count += 1
            finder[x.get("publicatienummer")] = x

        if opt%2 == 0:
            for t in finder.keys():
                if finder.get(t).get("type") == 0:
                    Command.handle_publication(t, tree, finder)
            print("Done publications, now subworks")
        else:
            print("skipping publication adding")

        if opt > 0:
            for t in finder.keys():
                if finder.get(t).get("type") == -1:
                    Command.handle_subwork(t, tree, finder)
            print("done subworks, now series")
            handled = []

            for t in finder.keys():
                if finder.get(t).get("type") == 1:
                    handled += Command.handle_series_node(handled, t, tree, finder, duds)
            print("done series, now adding works to series")
            for t in tree.keys():
                if finder.get(t).get("type") == 0 and finder.get(t).get("reeks_publicatienummer") > 0:
                    Command.handle_part_of_series(t, tree, finder, duds)

        mycursor.execute("SELECT * FROM band JOIN publicatie USING (publicatienummer);")
        banden = dict()
        for x in mycursor:
            banden[x.get("publicatienummer")] = x
        print("Now items")
        if opt%2 == 0:
            for k in Publication.objects.all():
                band = banden.get(k.old_id)

                if band is None:
                    print(k.old_id)
                    print(k.title)
                    print(banden.keys())
                else:
                    if len(Item.objects.filter(old_id=k.old_id)) > 0:
                        continue
                    s = band.get("sortering")
                    if s == "titel":
                        k.sorting = "TITLE"
                    else:
                        k.sorting = "AUTHOR"
                    k.save()
                    Item.objects.create(old_id=k.old_id, signature=band.get("signatuur"), publication=k, hidden=False,
                                        isbn10=band.get("isbn10"), isbn13=band.get("isbn13"),
                                        bought_date=band.get('inkoopdatum') or "1900-01-01",
                                        last_seen=band.get('laatst_gezien'), pages=band.get('pagina'))
            print("Work import done")
