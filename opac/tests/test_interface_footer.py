# coding: utf-8

from flask import url_for
from base import BaseTestCase

import utils


class FooterTestCase(BaseTestCase):

    def test_license_home(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """

        collection = utils.makeOneCollection({'license': 'BY/4.0'})

        with self.client as c:

            response = c.get(url_for('main.index'))

            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/index.html')

            self.assertIn('https://creativecommons.org/licenses/by/4.0/', response.data)
            self.assertIn('https://i.creativecommons.org/l/by/4.0/88x31.png', response.data)
            self.assertIn('Todo o conteúdo de localhost, exceto onde está identificado, está licenciado sob uma Licença Creative Commons.', response.data)

    def test_license_list_theme(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """

        collection = utils.makeOneCollection({'license': 'BY/4.0'})

        with self.client as c:

            response = c.get(url_for('main.collection_list_theme'))

            self.assertStatus(response, 200)

            self.assertTemplateUsed('collection/list_theme.html')

            self.assertIn('https://creativecommons.org/licenses/by/4.0/', response.data)
            self.assertIn('https://i.creativecommons.org/l/by/4.0/88x31.png', response.data)
            self.assertIn('Todo o conteúdo de localhost, exceto onde está identificado, está licenciado sob uma Licença Creative Commons.', response.data)

    def test_license_journal_home(self):
        """
        Testa se os links e o conteúdo da licença esta de acordo com a licença
        cadastrada na coleção.
        """

        collection = utils.makeOneCollection({'license': 'BY/4.0'})

        journal = utils.makeOneJournal()

        with self.client as c:

            response = c.get(url_for('main.journal_detail',
                                     journal_id=journal.id))

            self.assertStatus(response, 200)

            self.assertTemplateUsed('journal/detail.html')

            self.assertIn('https://creativecommons.org/licenses/by/4.0/', response.data)
            self.assertIn('https://i.creativecommons.org/l/by/4.0/88x31.png', response.data)
            self.assertIn('Todo o conteúdo de localhost, exceto onde está identificado, está licenciado sob uma Licença Creative Commons.', response.data)
