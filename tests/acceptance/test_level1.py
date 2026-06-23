"""Aceitação do nível 1 — fundamentos & FastAPI."""

from __future__ import annotations

import pytest

from app.levels.level1 import clamp_box


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"]
    assert body["version"]
    assert body["levels"] == [1, 2, 3, 4, 5]


def test_clamp_box_clamps_to_bounds():
    out = clamp_box([-10.0, -5.0, 700.0, 500.0], 640, 480)
    assert out == [0.0, 0.0, 640.0, 480.0]


def test_clamp_box_normalizes_inverted():
    out = clamp_box([100.0, 120.0, 40.0, 30.0], 640, 480)
    assert out[0] <= out[2] and out[1] <= out[3]
    assert 0 <= out[0] <= 640 and 0 <= out[2] <= 640


def test_clamp_box_does_not_mutate_input():
    src = [-10.0, -5.0, 700.0, 500.0]
    clamp_box(src, 640, 480)
    assert src == [-10.0, -5.0, 700.0, 500.0]


def test_image_metadata(client, png_bytes):
    data = png_bytes(320, 200)
    r = client.post("/image/metadata", files={"file": ("x.png", data, "image/png")})
    assert r.status_code == 200
    body = r.json()
    assert body["width"] == 320
    assert body["height"] == 200
    assert body["mode"] == "RGB"
    assert body["format"] == "PNG"


def test_image_metadata_rejects_non_image(client):
    r = client.post(
        "/image/metadata",
        files={"file": ("x.txt", b"this is not an image", "text/plain")},
    )
    assert r.status_code == 400, "um upload que não é imagem deve dar um 400 limpo, não um 500"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
