# coding: utf-8

from sqlalchemy.exc import IntegrityError
from webapp import dbsql, models

from .base import BaseTestCase


class UserModelTestCase(BaseTestCase):
    def test_create_user_with_valid_email_and_password_is_ok(self):
        """
        Com:
            - email e senha válidos
        Quando:
            - tentamos criar um novo usuário
        Verifcamos:
            - que o novo usuário é criado com sucesso
            - o campo email_confirmed é falso.
        """

        # with
        data = {
            "email": "foo@bar.com",
            "_password": "12345",
        }
        # when
        new_user = models.User(**data)
        dbsql.session.add(new_user)
        dbsql.session.commit()

        # then
        # pegamos o novo registro
        user_from_db = (
            dbsql.session.query(models.User).filter_by(email=data["email"]).first()
        )
        self.assertIsNotNone(user_from_db)
        self.assertEqual(data["email"], user_from_db.email)
        self.assertIsNotNone(user_from_db.password)
        self.assertFalse(user_from_db.email_confirmed)

    def test_user_model_unicode_is_the_email(self):
        """
        Com:
            - email e senha válida
        Quando:
            - tentamos criar um novo usuário
        Verifcamos:
            - que o novo usuário tem como __unicode__ o seu email
        """

        # with
        data = {
            "email": "foo@bar.com",
            "_password": "12345",
        }
        # when
        new_user = models.User(**data)
        # then
        self.assertEqual(data["email"], new_user.email)

    def test_create_user_with_valid_email_and_password_and_confirm_email_is_ok(self):
        """
        Com:
            - email e senha válidos
        Quando:
            - tentamos criar um novo usuário, indicando email_confirmed True
        Verifcamos:
            - que o novo usuário é criado com sucesso
            - o campo email_confirmed é true.
        """

        # with
        data = {
            "email": "foo@bar.com",
            "_password": "12345",
            "email_confirmed": True,
        }
        # when
        new_user = models.User(**data)
        dbsql.session.add(new_user)
        dbsql.session.commit()

        # then
        # pegamos o novo registro
        user_from_db = (
            dbsql.session.query(models.User).filter_by(email=data["email"]).first()
        )
        self.assertIsNotNone(user_from_db)
        self.assertEqual(data["email"], user_from_db.email)
        self.assertIsNotNone(user_from_db.password)
        self.assertTrue(user_from_db.email_confirmed)

    def test_create_user_with_valid_email_only_is_ok(self):
        """
        Com:
            - email válidos (sem senha)
        Quando:
            - tentamos criar um novo usuário
        Verifcamos:
            - que o novo usuário é criado com sucesso
            - o campo email_confirmed é falso.
        """

        # with
        data = {
            "email": "foo@bar.com",
        }
        # when
        new_user = models.User(**data)
        dbsql.session.add(new_user)
        dbsql.session.commit()

        # then
        user_from_db = (
            dbsql.session.query(models.User).filter_by(email=data["email"]).first()
        )
        self.assertIsNotNone(user_from_db)
        self.assertEqual(data["email"], user_from_db.email)
        self.assertIsNone(user_from_db.password)
        self.assertFalse(user_from_db.email_confirmed)

    def test_create_user_with_valid_password_only_raise_error(self):
        """
        Com:
            - email e senha válidos
        Quando:
            - tentamos criar um novo usuário
        Verifcamos:
            - da error de integridade.
        """

        # with
        data = {
            "_password": "12345",
        }
        # when
        new_user = models.User(**data)
        dbsql.session.add(new_user)
        # then
        with self.assertRaises(IntegrityError):
            dbsql.session.commit()

    def test_create_user_with_invalid_email_raise_error(self):
        """
        Com:
            - email do usuário que já existe
        Quando:
            - tentamos criar um novo usuário
        Verifcamos:
            - da error de integridade.
        """

        # with
        data = {
            "email": None,
        }
        # when
        new_user = models.User(**data)
        dbsql.session.add(new_user)
        # then
        with self.assertRaises(IntegrityError):
            dbsql.session.commit()

    def test_is_correct_password_using_the_same_password_return_true(self):
        """
        Com:
            - um usuário com email e senha
        Quando:
            - Criamos um novo usuário
            - invocamos o método: is_correct_password com a mesma senha
        Verifcamos:
            - o retorno é True
        """

        # with
        data = {
            "email": "foo@bar.com",
            "_password": "12345",
        }
        # when
        new_user = models.User(**data)
        new_user.define_password(data["_password"])
        # then
        self.assertTrue(new_user.is_correct_password(data["_password"]))

    def test_is_correct_password_using_different_password_return_false(self):
        """
        Com:
            - um usuário com email e senha
        Quando:
            - Criamos um novo usuário
            - invocamos o método: is_correct_password com uma senha diferente
        Verifcamos:
            - o retorno é False
        """

        # with
        data = {
            "email": "foo@bar.com",
            "_password": "12345",
        }
        # when
        new_user = models.User(**data)
        # then
        self.assertFalse(new_user.is_correct_password("54321"))

    def test_is_correct_password_when_user_has_no_password_return_false(self):
        """
        Com:
            - um usuário sem senha
        Quando:
            - invocamos o método: is_correct_password com alguma senha
        Verifcamos:
            - o retorno é true
        """

        # with
        data = {
            "email": "foo@bar.com",
        }
        # when
        new_user = models.User(**data)
        # then
        self.assertFalse(new_user.is_correct_password("xyz"))

    def test_is_correct_password_with_none_when_user_has_no_password_return_false(self):
        """
        Com:
            - um usuário sem senha
        Quando:
            - invocamos o método: is_correct_password com alguma senha
        Verifcamos:
            - o retorno é true
        """

        # with
        data = {
            "email": "foo@bar.com",
        }
        # when
        new_user = models.User(**data)
        # then
        self.assertFalse(new_user.is_correct_password(None))

    def test_user_with_email_send_confirmation_email_works(self):
        """
        Com:
            - um usuário com email
        Quando:
            - invocamos o método: send_confirmation_email
        Verifcamos:
            - o retorno da função indica sucesso
        """

        # with
        data = {
            "email": "foo@bar.com",
        }
        # when
        new_user = models.User(**data)
        # then
        expected_response = (True, "")
        self.assertEqual(expected_response, new_user.send_confirmation_email())

    def test_user_without_email_send_confirmation_email_works(self):
        """
        Com:
            - um usuário sem email
        Quando:
            - invocamos o método: send_confirmation_email
        Verifcamos:
            - o metodo retorna ValueError
        """

        # with
        data = {
            "email": None,
        }
        # when
        new_user = models.User(**data)
        # then
        with self.assertRaises(ValueError):
            self.assertFalse(new_user.send_confirmation_email())

    def test_user_with_email_send_reset_password_email_works(self):
        """
        Com:
            - um usuário com email
        Quando:
            - invocamos o método: send_reset_password_email
        Verifcamos:
            - o retorno da função indica sucesso
        """

        # with
        data = {
            "email": "foo@bar.com",
        }
        # when
        new_user = models.User(**data)
        # then
        expected_response = (True, "")
        self.assertEqual(expected_response, new_user.send_reset_password_email())

    def test_user_without_email_send_reset_password_email_works(self):
        """
        Com:
            - um usuário sem email
        Quando:
            - invocamos o método: send_reset_password_email
        Verifcamos:
            - o metodo retorna ValueError
        """

        # with
        data = {
            "email": None,
        }
        # when
        new_user = models.User(**data)
        # then
        with self.assertRaises(ValueError):
            self.assertFalse(new_user.send_reset_password_email())


class LoadUserTestCase(BaseTestCase):
    def test_valid_user_return_the_user(self):
        """
        Com:
            - um usuário válido
        Quando:
            - cadastramos o novo usuário
            - invocamos o método: load_user
        Verifcamos:
            - o retorno é o usuário cadastrado
        """

        # with
        data = {
            "email": "foo@bar.com",
        }
        # when
        new_user = models.User(**data)
        dbsql.session.add(new_user)
        dbsql.session.commit()

        # then
        user_from_db = (
            dbsql.session.query(models.User).filter_by(email=data["email"]).first()
        )
        user_loaded = models.load_user(user_from_db.id)
        self.assertEqual(user_from_db.email, user_loaded.email)

    def test_invalid_user_raise_error(self):
        """
        Quando:
            - invocamos o método: load_user, com qualquer id
        Verifcamos:
            - levanta uma exception
        """
        fake_id = 1234
        user_loaded = models.load_user(fake_id)
        self.assertIsNone(user_loaded)
