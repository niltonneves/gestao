import pytest

from app import create_app
from app.config import Config
from app.extensions import db

TEST_DATABASE_URI = "sqlite:////tmp/opencode/n7_test_gestao.db"


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URI


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_primeiro_acesso_page(client):
    resp = client.get("/auth/primeiro-acesso")
    assert resp.status_code == 200


def test_login_flow(client):
    resp = client.post(
        "/auth/primeiro-acesso",
        data={
            "nome": "Administrador Teste",
            "email": "admin@teste.com",
            "senha": "123456",
            "confirmar": "123456",
            "razao_social": "Empresa Teste LTDA",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    resp = client.post(
        "/auth/login",
        data={"email": "admin@teste.com", "senha": "123456"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
