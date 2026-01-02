from django.db import models

from django.contrib.postgres.indexes import GinIndex

class TrigramIndex(GinIndex):
    def get_sql_create_template_values(self, model, schema_editor, using):
        fields = [model._meta.get_field(field_name) for field_name, order in self.fields_orders]
        tablespace_sql = schema_editor._get_index_tablespace_sql(model, fields)
        quote_name = schema_editor.quote_name
        columns = [
            ('%s %s' % (quote_name(field.column), order)).strip() + ' gin_trgm_ops'
            for field, (field_name, order) in zip(fields, self.fields_orders)
        ]
        return {
            'table': quote_name(model._meta.db_table),
            'name': quote_name(self.name),
            'columns': ', '.join(columns),
            'using': using,
            'extra': tablespace_sql,
        }

class SearchWord(models.Model):
    word = models.CharField(max_length=255, db_index=True, unique=True)

    @staticmethod
    def get_word(word):
        return SearchWord.objects.get_or_create(word=word)[0]

    class Meta:
        indexes = [
            TrigramIndex(fields=['word'])
        ]