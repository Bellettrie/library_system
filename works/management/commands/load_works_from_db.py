import datetime

import mysql.connector

from django.core.management.base import BaseCommand, CommandError

from series.models import Series, WorkInSeries, SeriesNode
from works.models import Work, WorkInPublication, Publication, SubWork


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    @staticmethod
    def handle_publication(publication, tree, finder):
        data = finder.get(publication)
        print(publication)
        Publication.objects.create(title=data.get("titel"),
                                   sub_title=data.get("subtitel").decode("utf-8"),
                                   language=data.get("taal").decode("utf-8"),
                                   is_translated=data.get("is_vertaald"),
                                   original_title=data.get("orig_titel").decode("utf-8"),
                                   original_subtitle=data.get("orig_subtitel").decode("utf-8"),
                                   original_language=data.get("orig_taal").decode("utf-8"),
                                   hidden=data.get("verbergen"),
                                   date_added=data.get("gecatalogiseerd") or datetime.datetime.today(),
                                   comment=data.get("commentaar"),
                                   internal_comment=data.get("intern_commentaar"),
                                   signature_fragment=data.get("signatuurfragment").decode("utf-8"),
                                   old_id=publication)

    @staticmethod
    def handle_subwork(sub_work, tree, finder):
        data = finder.get(sub_work)
        print(sub_work)
        work = SubWork.objects.create(title=data.get("titel"),
                                      sub_title=data.get("subtitel").decode("utf-8"),
                                      language=data.get("taal").decode("utf-8"),
                                      is_translated=data.get("is_vertaald"),
                                      original_title=data.get("orig_titel").decode("utf-8"),
                                      original_subtitle=data.get("orig_subtitel").decode("utf-8"),
                                      original_language=data.get("orig_taal").decode("utf-8"),
                                      hidden=data.get("verbergen"),
                                      date_added=data.get("gecatalogiseerd") or datetime.datetime.today(),
                                      comment=data.get("commentaar"),
                                      internal_comment=data.get("intern_commentaar"),
                                      signature_fragment=data.get("signatuurfragment").decode("utf-8"),
                                      old_id=sub_work)
        WorkInPublication.objects.create(work=work, publication=Publication.objects.get(
            old_id=tree.get(sub_work)), number_in_publication=int(data.get("reeks_deelnummer")),
                                         display_number_in_publication=data.get("reeks_deelaanduiding").decode("utf-8"))

    @staticmethod
    def handle_series_node(handled, node, tree, finder):
        if node in handled:
            return []
        data = finder.get(node)
        tt = data.get("type")
        if tt != 1:
            print(finder.get(node))
        handled_list = []
        nr = finder.get(node).get("reeks_publicatienummer")
        if nr > 0:
            handled_list += Command.handle_series_node(handled, nr, tree, finder)
        if data.get("reeks_publicatienummer") > 0:
            print(node)
            super_series = Series.objects.get(old_id=data.get("reeks_publicatienummer"))
            Series.objects.create(part_of_series=super_series, number=int(data.get("reeks_deelnummer")),
                                  display_number=data.get(
                                      "reeks_deelaanduiding").decode("utf-8"), old_id=node)
        else:
            Series.objects.create(number=int(data.get("reeks_deelnummer")),
                                  display_number=data.get(
                                      "reeks_deelaanduiding").decode("utf-8"), old_id=node)
            print(node)

        handled_list.append(node)

        return handled_list

    @staticmethod
    def handle_part_of_series(publication, tree, finder):
        data = finder.get(publication)
        pub = data.get("reeks_publicatienummer")
        print(pub)
        series_data = finder.get(pub)
        print(series_data)
        if series_data.get("type") != 1:
            return
        ser = SeriesNode.objects.get(old_id=pub)
        work = Work.objects.get(old_id=publication)
        WorkInSeries.objects.create(part_of_series=ser, old_id=publication, work=work, number=int(data.get("reeks_deelnummer")),
                                    display_number=data.get(
                                        "reeks_deelaanduiding").decode("utf-8"))

    def handle(self, *args, **options):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="oldsystem"
        )
        mycursor = mydb.cursor(dictionary=True)

        tree = dict()
        finder = dict()
        mycursor.execute("SELECT * FROM publicatie")

        count = 0
        for x in mycursor:
            if x.get("reeks_publicatienummer") > 0:
                tree[x.get("publicatienummer")] = x.get("reeks_publicatienummer")
                count += 1
            finder[x.get("publicatienummer")] = x

        for t in finder.keys():
            if finder.get(t).get("type") == 0:
                Command.handle_publication(t, tree, finder)

        for t in finder.keys():
            if finder.get(t).get("type") == -1:
                Command.handle_subwork(t, tree, finder)

        handled = []

        for t in finder.keys():
            if finder.get(t).get("type") == 1:
                handled += Command.handle_series_node(handled, t, tree, finder)

        for t in tree.keys():
            if finder.get(t).get("type") == 0 and finder.get(t).get("reeks_publicatienummer") > 0:
                Command.handle_part_of_series(t, tree, finder)
